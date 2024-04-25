from flask import Flask, request
from route_creation.route_creator import generate_rated_route

app = Flask(__name__)

@app.route('/generate-route', methods=['POST'])
def generate_route():
    request_data = request.get_json().get('data', "No data found")
    return generate_rated_route(request_data['start'], request_data['end'], request_data['geoJson'])

if __name__ == '__main__':
    app.run(port=3500, host='0.0.0.0', debug=True)
