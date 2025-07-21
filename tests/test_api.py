import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_evaluate_and_result(client):
    # Submit an expression
    response = client.post('/evaluate', json={'expression': '2+2'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'request_id' in data

    # Poll for the result
    req_id = data['request_id']
    for _ in range(10):
        result_resp = client.get(f'/result/{req_id}')
        if result_resp.status_code == 200:
            result_data = result_resp.get_json()
            assert result_data['result'] == '4'
            break
        assert result_resp.status_code == 202