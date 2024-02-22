import json

def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Hello, World!'

def test_hello_world_post(client):
    hdr = {'Content-Type': 'application/json'}
    response = client.get('/test', headers=hdr)
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'No data found'

    response = client.post('/test', headers=hdr, json={'data': 'some_data'})
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {'data': 'some_data'}  