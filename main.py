from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'


@app.route('/svm', methods=['GET','POST'])
def hello_world_post():
    request_data = request.get_json().get('data', "No data found")
    
    return jsonify({'data': request_data})


@app.route('/bert', methods=['GET','POST'])
def hello_world_post():
    request_data = request.get_json().get('data', "No data found")
    
    return jsonify({'data': request_data})


@app.route('/lr', methods=['GET','POST'])
def hello_world_post():
    request_data = request.get_json().get('data', "No data found")
    
    return jsonify({'data': request_data})