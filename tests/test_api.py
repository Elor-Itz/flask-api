import pytest
import time
from utils.stream import Stream
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

# Health endpoint test
def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'

# Standard expression tests
def test_evaluate_and_result(client):
    response = client.post('/evaluation/expression', json={'expression': '2+2'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '4'
            break
        assert result_resp.status_code == 202

def test_power_operation_standard(client):
    response = client.post('/evaluation/expression', json={'expression': '2^5+1'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '33'
            break
        assert result_resp.status_code == 202

def test_parser_parentheses(client):
    response = client.post('/evaluation/expression', json={'expression': '(2+3)*4'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '20'
            break
        assert result_resp.status_code == 202

def test_parser_unary_minus(client):
    response = client.post('/evaluation/expression', json={'expression': '-5+2'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '-3'
            break
        assert result_resp.status_code == 202

def test_parser_division_by_zero(client):
    response = client.post('/evaluation/expression', json={'expression': '2/0'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert 'error' in result_data
            assert 'division' in result_data['error'] or 'ZeroDivisionError' in result_data['error']
            break
        assert result_resp.status_code == 202

def test_invalid_expression(client):
    response = client.post('/evaluation/expression', json={'expression': '2++2'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

# Variable expression tests
def test_evaluate_variable_and_result(client):
    response = client.post('/evaluation/variable', json={'expression': 'x*2', 'value': 5})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '10'
            break
        assert result_resp.status_code == 202

def test_power_operation_variable(client):
    response = client.post('/evaluation/variable', json={'expression': 'x^2 + 2*x + 1', 'value': 3})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '16'
            break
        assert result_resp.status_code == 202

def test_variable_parser_implicit_multiplication(client):
    response = client.post('/evaluation/variable', json={'expression': '2x+1', 'value': 4})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/evaluation/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '9'
            break
        assert result_resp.status_code == 202

def test_invalid_variable_expression(client):
    response = client.post('/evaluation/variable', json={'expression': 'x++2', 'value': 5})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_variable_parser_invalid_characters(client):
    response = client.post('/evaluation/variable', json={'expression': 'x*2a', 'value': 5})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

# Result endpoint status test
def test_result_processing_status(client):
    response = client.post('/evaluation/expression', json={'expression': '2+2'})
    req_id = response.get_json()['request_id']
    result_resp = client.get(f'/evaluation/result/{req_id}')
    data = result_resp.get_json()
    if result_resp.status_code == 202:
        assert data['status'] == 'processing'
    elif result_resp.status_code == 200:
        assert 'result' in data or 'error' in data
    else:
        assert False, f"Unexpected status code: {result_resp.status_code}"

# Stream utility tests
def test_stream_add_and_forEach():
    results = []
    s = Stream()
    s.forEach(lambda x: results.append(x))
    s.add(1)
    s.add(2)
    time.sleep(0.1)  # Give the thread time to process
    assert results == [1, 2]
    s.stop()

def test_stream_apply_true_false():
    results = []
    s = Stream()
    next_s = s.apply(lambda x: x > 0)
    next_s.forEach(lambda x: results.append(x))
    s.add(1)
    s.add(-1)
    s.add(2)
    time.sleep(0.1)
    assert results == [1, 2]
    s.stop()
    next_s.stop()

def test_stream_apply_custom_value():
    results = []
    s = Stream()
    next_s = s.apply(lambda x: x * 2 if x < 5 else False)
    next_s.forEach(lambda x: results.append(x))
    s.add(2)
    s.add(6)
    s.add(3)
    time.sleep(0.1)
    assert results == [4, 6]
    s.stop()
    next_s.stop()

def test_stream_stop():
    s = Stream()
    s.forEach(lambda x: None)
    s.stop()
    assert s.stop_flag is True