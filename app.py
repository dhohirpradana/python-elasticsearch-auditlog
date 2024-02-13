from flask import Flask, request, jsonify
import datetime
import requests
import os
import json
import traceback

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


def log_request(path):
    print("path", path)
    log_data_f = {}
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    log_data = {
        'timestamp': now,
        'method': request.method,
        'url': request.url.replace(my_url, ''),
        'headers': dict(request.headers),
    }

    url = path
    max_length = 20

    # join url and query string
    if request.query_string:
        url = url + '?' + request.query_string.decode('utf-8')

    print("url", url)

    # check if data is form data or json
    def to_json():
        # if request.headers['Content-Type'] contains 'application/x-www-form-urlencoded' or 'multipart/form-data'
        if 'multipart/form-data' in request.headers['Content-Type'] or 'application/x-www-form-urlencoded' in request.headers['Content-Type']:
            # to json format
            return dict(request.form)
        return json.loads(request.get_data().decode('utf-8'))

    def save_log(r):
        status_code = r.status_code
        log_data_f['req'] = log_data
        try:
            data = r.json()
        except:
            data = ''
        res = {
            'message': "Success",
            'data': data,
            'status_code': status_code
        }
        log_data_f['res'] = res
        es_handler(log_data_f)

    headers = dict(request.headers)
    keys_to_remove = ['Content-Type', 'User-Agent', 'Accept', 'Postman-Token',
                      'Host', 'Accept-Encoding', 'Connection', 'Content-Length']

    headers = {key: value for key,
               value in headers.items() if key not in keys_to_remove}

    try:
        if request.method.lower() == 'post':
            log_data['data'] = to_json()
            # teruskan
            if 'content' in log_data['data']:
                if len(log_data['data']['content']) > max_length:
                    log_data['data']['content'] = log_data['data']['content'][:max_length] + \
                        '...and ' + \
                        str(len(log_data['data']['content']) -
                            max_length) + ' char'
            response = requests.post(url, headers=headers,
                                     json=to_json(), verify=False)

            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(
                    f"Request failed with status code {response.status_code}: {response.json()}")

            save_log(response)

            return jsonify(response.json()), response.status_code

        if request.method.lower() == 'get':
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(
                    f"Request failed with status code {response.status_code}: {response.json()}")

            save_log(response)

            return jsonify(response.json()), response.status_code

        if request.method.lower() == 'put':
            response = requests.put(url, headers=headers, json=to_json())
            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(
                    f"Request failed with status code {response.status_code}: {response.json()}")

            save_log(response)

            return jsonify(response.json()), response.status_code

        if request.method.lower() == 'patch':
            response = requests.patch(url, headers=headers, json=to_json())
            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(
                    f"Request failed with status code {response.status_code}: {response.json()}")

            save_log(response)

            return jsonify(response.json()), response.status_code

        if request.method.lower() == 'delete':
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(
                    f"Request failed with status code {response.status_code}: {response.json()}")

            save_log(response)

            return jsonify(response.json()), response.status_code

    except requests.HTTPError as e:
        print(e)
        return jsonify({"message": str(e)}), 500

    # try:
    #     if request.method.lower() == 'get':
    #         r = requests.get(url, headers=headers)
    #     elif request.method.lower() == 'post':
    #         log_data['data'] = to_json()
    #         if 'content' in log_data['data']:
    #             if len(log_data['data']['content']) > max_length:
    #                 log_data['data']['content'] = log_data['data']['content'][:max_length] + \
    #                     '...and ' + \
    #                     str(len(log_data['data']['content']) -
    #                         max_length) + ' char'
    #         r = requests.post(url, headers=headers, json=to_json())
    #     elif request.method.lower() == 'put':
    #         log_data['data'] = to_json()
    #         if 'content' in log_data['data']:
    #             if len(log_data['data']['content']) > max_length:
    #                 log_data['data']['content'] = log_data['data']['content'][:max_length] + \
    #                     '...and ' + \
    #                     str(len(log_data['data']['content']) -
    #                         max_length) + ' char'
    #         r = requests.put(url, headers=headers, json=to_json())
    #     elif request.method.lower() == 'patch':
    #         log_data['data'] = to_json()
    #         if 'content' in log_data['data']:
    #             if len(log_data['data']['content']) > max_length:
    #                 log_data['data']['content'] = log_data['data']['content'][:max_length] + \
    #                     '...and ' + \
    #                     str(len(log_data['data']['content']) -
    #                         max_length) + ' char'
    #         r = requests.patch(url, headers=headers, json=to_json())
    #     elif request.method.lower() == 'delete':
    #         r = requests.delete(url, headers=headers)
    #     else:
    #         print("Invalid method specified")
    #         return jsonify({"message": "Invalid method specified"}), 400

    #     r.raise_for_status()
    #     status_code = r.status_code
    #     log_data_f['req'] = log_data
    #     try:
    #         data = r.json()
    #     except:
    #         data = ''
    #     res = {
    #         'message': "Success",
    #         'status_code': status_code
    #     }
    #     log_data_f['res'] = res
    #     es_handler(log_data_f)
    #     return jsonify(data), status_code

    # except requests.HTTPError as e:
    #     status_code = e.response.status_code
    #     log_data_f['req'] = log_data
    #     res = {
    #         'message': str(e),
    #         'status_code': status_code
    #     }
    #     log_data_f['res'] = res
    #     print("Error message:", e)
    #     print("log_data_f", log_data_f)
    #     es_handler(log_data_f)
    #     return jsonify({"message": str(e)}), status_code

    # except Exception as e:
    #     print("Error:", e)
    #     traceback_info = traceback.format_exc()

    #     print(traceback_info)
    #     return jsonify({"message": str(e)}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def catch_all(path):
    validate_envs()
    return log_request(path)

# test


@app.route('/test', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def test():
    data = dict(request.form.to_dict(flat=False))
    print(data)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
