from flask import Flask, Response, request
import requests
import os

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

# 🔧 Main block to bind to correct host and port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render uses $PORT
    app.run(host='0.0.0.0', port=port)
