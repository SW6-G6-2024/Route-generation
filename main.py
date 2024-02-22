from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'


@app.route('/test', methods=['GET','POST'])
def hello_world_post():
    if request.method == 'GET':
        return 'No data found', 400
    elif request.method == 'POST':
      request_data = request.get_json()
      if not request_data:
            # If request body is empty, return a specific response
            return 'Empty request body', 400
      return jsonify(request_data)


if __name__ == "__main__":
    app.run()