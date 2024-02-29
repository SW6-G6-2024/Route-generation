from flask import Flask, request
from .data_formatter import data_formatter
from .route_creator import generate_shortest_route

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'


@app.route('/test', methods=['GET','POST'])
def hello_world_post():
    request_data = request.get_json().get('data', "No data found")
    
    return data_formatter(request_data)

@app.route('/generate-route', methods=['POST'])
def generate_route():
    request_data = request.get_json().get('data', "No data found")
    return generate_shortest_route(request_data['start'], request_data['end'], request_data['geoJson'])

if __name__ == '__main__':
    app.run(port=3500, host='0.0.0.0', debug=True)
