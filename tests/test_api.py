import pytest
from app import app, db

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create tables once per test session and drop after."""
    with app.app_context():
        db.create_all()
    yield
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Start the stream processor only once per test session
        from routes import expression_stream, process_expression
        # Use a flag to ensure the stream is only started once
        if not hasattr(expression_stream, "_started"):
            expression_stream.forEach(lambda item: process_expression(item, app))
            expression_stream._started = True
        yield client

def test_evaluate_and_result(client):
    # Submit an expression
    response = client.post('/evaluation/expression', json={'expression': '2+2'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data

    # Poll for the result
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '4'
            break
        assert result_resp.status_code == 202

def test_invalid_expression(client):
    response = client.post('/evaluation/expression', json={'expression': '2++2'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_evaluate_variable_and_result(client):
    # Submit a variable expression
    response = client.post('/evaluation/variable', json={'expression': 'x*2', 'value': 5})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data

    # Poll for the result
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '10'
            break
        assert result_resp.status_code == 202

def test_invalid_variable_expression(client):
    response = client.post('/evaluation/variable', json={'expression': 'x++2', 'value': 5})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_result_processing_status(client):
    response = client.post('/evaluation/expression', json={'expression': '2+2'})
    req_id = response.get_json()['request_id']
    result_resp = client.get(f'/evaluation/result/{req_id}')
    assert result_resp.status_code == 202
    data = result_resp.get_json()
    assert data['status'] == 'processing'

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'