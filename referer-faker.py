from flask import Flask, Response, request
import requests
import os

app = Flask(__name__)

# The real Gaitspace backend
GAITSPACE_BASE = "https://fc9ae48bc0a4-search-app.gaitspace.net"
FAKE_REFERER = "https://stmarketing.isracard.co.il"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    # Build full target URL
    target_url = f"{GAITSPACE_BASE}/{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"

    # Forward browser headers and override Referer
    headers = {
        'Referer': FAKE_REFERER,
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Content-Type': request.headers.get('Content-Type', ''),
    }

    # Proxy method
    method = request.method.lower()
    req_func = getattr(requests, method)

    try:
        resp = req_func(
            target_url,
            headers=headers,
            data=request.get_data(),
            stream=True,
            timeout=10
        )

        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection']
        response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers}

        return Response(resp.content, status=resp.status_code, headers=response_headers)
    except Exception as e:
        return f"Proxy error: {e}", 500

# Required for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
