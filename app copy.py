import datetime
import os
from flask import Flask, request, jsonify
import requests

from flask_cors import CORS
from elastic import handler as es_handler

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

required_env_vars = ["ELASTIC_URL", "MY_URL"]
my_url = os.environ.get('MY_URL')


def validate_envs():
    for env_var in required_env_vars:
        if env_var not in os.environ:
            raise EnvironmentError(
                f"Required environment variable {env_var} is not set.")


def check_res_json(rj):
    try:
        data = rj.json()
    except:
        data = None

    return data

# check if data is form data or json


def to_json():
    # print(request.form)
    # if request.headers['Content-Type'] contains 'application/x-www-form-urlencoded' or 'multipart/form-data'
    if request.form:
        # Filter values exceeding 100 characters
        filtered_form_data = {key: value[:100]
                              for key, value in request.form.items()}

        print("FILTERED", dict(filtered_form_data))

        # Convert to JSON format
        return dict(filtered_form_data)

    else:
        print("JSON DATA")
        return request.get_json()


def save_log(r, log_data):
    status_code = r.status_code
    log_data_f = {}
    log_data_f['req'] = log_data
    try:
        data = r.json()
    except:
        data = None
    res = {
        'message': "Success",
        'data': data,
        'status_code': status_code
    }
    log_data_f['res'] = res
    es_handler(log_data_f)


def log_request(path):
    print("path", path)
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    log_data = {
        'timestamp': now,
        'method': request.method,
        'url': request.url.replace(my_url, ''),
        'headers': dict(request.headers),
    }

    url = path

    # join url and query string
    if request.query_string:
        url = url + '?' + request.query_string.decode('utf-8')

    if "bodha.co.id" in url:
        url = url.replace("https://", "http://")

    print("url", url)
    print("REQUEST", request.data)

    headers = dict(request.headers)
    keys_to_remove = ['Content-Type', 'User-Agent', 'Accept', 'Postman-Token',
                      'Host', 'Accept-Encoding', 'Connection', 'Content-Length']

    headers = {key: value for key,
               value in headers.items() if key not in keys_to_remove}

    try:
        if request.method.lower() == 'post':
            log_data['data'] = to_json()

            response = requests.post(url, headers=headers,
                                     json=to_json(), verify=False, timeout=60)

            data = check_res_json(response)

            save_log(response, log_data)

            return jsonify(data), response.status_code

        if request.method.lower() == 'get':
            response = requests.get(
                url, headers=headers, verify=False, timeout=60)

            data = check_res_json(response)

            print("DATA:", data)

            save_log(response, log_data)

            return data, response.status_code

        if request.method.lower() == 'put':
            log_data['data'] = to_json()

            response = requests.put(
                url, headers=headers, json=to_json(), verify=False, timeout=60)

            data = check_res_json(response)

            save_log(response, log_data)

            return jsonify(data), response.status_code

        if request.method.lower() == 'patch':
            log_data['data'] = to_json()

            response = requests.patch(
                url, headers=headers, json=to_json(), verify=False, timeout=60)

            data = check_res_json(response)

            save_log(response, log_data)

            return jsonify(data), response.status_code

        if request.method.lower() == 'delete':
            response = requests.delete(
                url, headers=headers, verify=False, timeout=60)

            data = check_res_json(response)

            save_log(response, log_data)
            return jsonify(data), response.status_code

    except requests.HTTPError as e:
        print(e)
        return jsonify({"message": str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def catch_all(path):
    if not path.startswith(('http://', 'https://')):
        return jsonify(None), 200

    validate_envs()
    data, code = log_request(path)
    return jsonify(data), code

# test


@app.route('/test', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def test():
    data = dict(request.form.to_dict(flat=False))
    print(data)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
