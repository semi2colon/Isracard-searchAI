from flask import Flask, Response, request
import requests

app = Flask(__name__)

TARGET_URL = "https://fc9ae48bc0a4-search-app.gaitspace.net"
FAKE_REFERER = "https://stmarketing.isracard.co.il/"

@app.route('/')
def proxy_iframe():
    headers = {
        'Referer': FAKE_REFERER,
        'User-Agent': request.headers.get('User-Agent')
    }
    resp = requests.get(TARGET_URL, headers=headers)
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))
