from flask import jsonify

def data_formatter(data):
    
    # Format the data to csv

    return jsonify({'data': data})