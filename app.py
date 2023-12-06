from flask import Flask, request, jsonify
import datetime
import requests
import os
import json

from flask_cors import CORS
from elastic import handler as es_handler

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

required_env_vars = ["ELASTIC_URL"]

def validate_envs():
    for env_var in required_env_vars:
        if env_var not in os.environ:
            raise EnvironmentError(
                f"Required environment variable {env_var} is not set.")

def log_request(path):
    log_data_f = {}
    log_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
    }
    
    url = path
    
    try:
        headers = dict(request.headers)
        keys_to_remove = ['Content-Type', 'User-Agent', 'Accept', 'Postman-Token', 'Host', 'Accept-Encoding', 'Connection', 'Content-Length']
        
        headers = {key: value for key, value in headers.items() if key not in keys_to_remove}

        if request.method.lower() == 'get':
            r = requests.get(url, headers=headers)
        elif request.method.lower() == 'post':
            log_data['data'] = json.loads(request.get_data().decode('utf-8'))
            r = requests.post(url, headers=headers, json=request.get_data().decode('utf-8'))
        elif request.method.lower() == 'put':
            log_data['data'] = json.loads(request.get_data().decode('utf-8'))
            r = requests.put(url, headers=headers, json=request.get_data().decode('utf-8'))
        elif request.method.lower() == 'patch':
            log_data['data'] = json.loads(request.get_data().decode('utf-8'))
            r = requests.patch(url, headers=headers, json=request.get_data().decode('utf-8'))
        elif request.method.lower() == 'delete':
            r = requests.delete(url, headers=headers)
        else:
            print("Invalid method specified")
            return jsonify({"message": "Invalid method specified"}), 400
        
        r.raise_for_status()
        status_code = r.status_code
        log_data_f['req'] = log_data
        data = r.json()
        res = {
            'data': data,
            'status_code': status_code
        }
        log_data_f['res'] = res
        es_handler(log_data_f)
        return jsonify({"message": "Success"}), status_code
        
    except requests.HTTPError as e:
        status_code = e.response.status_code
        log_data_f['req'] = log_data
        data = r.json()
        res = {
            'data': data,
            'status_code': status_code
        }
        log_data_f['res'] = res
        print("Error message:", e)
        es_handler(log_data_f)
        return jsonify({"message": str(e)}), status_code
        
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def catch_all(path):
    validate_envs()
    return log_request(path)

if __name__ == '__main__':
    app.run(debug=True)
