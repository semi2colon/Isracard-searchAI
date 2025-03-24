from flask import Flask, Response, request
import requests
import os

app = Flask(__name__)

# Real search engine host
TARGET_BASE = "https://fc9ae48bc0a4-search-app.gaitspace.net"
FAKE_REFERER = "https://stmarketing.isracard.co.il"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def full_proxy(path):
    # Build full target URL with query string
    target_url = f"{TARGET_BASE}/{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"

    # Headers
    headers = {
        'Referer': FAKE_REFERER,
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
        'Accept': request.headers.get('Accept', '*/*'),
    }

    # Pick the method dynamically
    method = request.method.lower()
    req_func = getattr(requests, method)

    try:
        # Send the request
        resp = req_func(
            target_url,
            headers=headers,
            data=request.get_data(),
            stream=True,
            timeout=15
        )

        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection']
        response_headers = {
            k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers
        }

        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except Exception as e:
        return f"Proxy error: {e}", 500

# Bind to proper port for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
