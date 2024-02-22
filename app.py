import datetime
from flask import Flask, request, jsonify
import requests
from elastic import handler as elastic_handler

app = Flask(__name__)


def to_json():
    if request.form:
        filtered_form_data = {key: value[:100]
                              for key, value in request.form.items()}

        print("FILTERED", dict(filtered_form_data))

        return dict(filtered_form_data)

    else:
        print("JSON DATA")
        return request.get_json()


@app.route('/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(url):
    full_url = f'{url}'

    if request.query_string:
        full_url += f'?{request.query_string.decode("utf-8")}'

    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    log_data = {
        'timestamp': now,
        'method': request.method,
        'url': full_url,
    }

    headers = dict(request.headers)

    data = to_json()

    if data is None:
        data = None

    files = []

    # print files names and sizes if any
    if request.files:
        for file in request.files:
            files.append({
                'name': file,
                'size': request.files[file].content_length
            })

    # Make the request
    response = requests.request(
        method=request.method,
        url=full_url,
        headers=headers,
        data=data,
        cookies=request.cookies,
        files=request.files,
        allow_redirects=False,
        verify=False,
        timeout=60
    )

    # Check if the response is JSON
    try:
        response_data = response.json()
    except ValueError:
        response_data = response.text

    log_data['req'] = {
        'headers': dict(request.headers),
        'data': data,
        'cookies': request.cookies,
        'files': files
    }

    log_data['res'] = {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'data': response_data
    }

    elastic_handler(log_data)

    return jsonify(response_data), response.status_code


if __name__ == '__main__':
    app.run(port=5000)
