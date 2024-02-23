import datetime
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from elastic import handler as elastic_handler

app = Flask(__name__)
CORS(app, origins="*")


def to_json():
    if request.form:
        filtered_form_data = {key: value[:100]
                              for key, value in request.form.items()}

        print("FILTERED", dict(filtered_form_data))

        return dict(filtered_form_data)

    else:
        print("JSON DATA")
        print(request.get_json())
        return request.get_json()


@app.route('/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(url):
    s = requests.Session()

    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.'}
    s.headers.update(header)

    full_url = f'{url}'

    if request.query_string:
        full_url += f'?{request.query_string.decode("utf-8")}&antibot=true&premium_proxy=true&proxy_country=us'

    print("FULL URL", full_url)

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
    response = s.request(
        method=request.method,
        url=full_url,
        headers=headers,
        # data=data,
        json=data,
        cookies=request.cookies,
        files=files
    )

    try:
        response_data = response.json()
        de = response_data
    except ValueError:
        response_data = response.text
        de = {
            'text': response_data
        }

    print("RESPONSE", response_data)

    log_data['req'] = {
        'headers': dict(request.headers),
        'data': data,
        'cookies': request.cookies,
        'files': files
    }

    log_data['res'] = {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'data': de
    }

    elastic_handler(log_data)

    return jsonify(response_data), response.status_code


if __name__ == '__main__':
    app.run(port=5000)
