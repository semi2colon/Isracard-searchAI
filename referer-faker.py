from flask import Flask, Response, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Config
TARGET_BASE = "https://fc9ae48bc0a4-search-app.gaitspace.net"
FAKE_REFERER = "https://stmarketing.isracard.co.il"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def full_proxy(path):
    target_url = f"{TARGET_BASE}/{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"

    method = request.method.lower()
    req_func = getattr(requests, method)

    # 🔐 Spoof required headers
    headers = {
        'Referer': FAKE_REFERER,
        'Origin': TARGET_BASE,  # 🔑 KEY FIX!
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Content-Type': request.headers.get('Content-Type', ''),
    }

    try:
        # 🟡 Log request
        print("\n--- 🟡 Incoming Request ----------------------------")
        print(f"🔸 METHOD:  {request.method}")
        print(f"🔸 PATH:    /{path}")
        print(f"🔸 TARGET:  {target_url}")
        if request.data:
            print(f"🔸 BODY:    {request.get_data(as_text=True)}")

        # Make the request
        resp = req_func(
            target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True,
            timeout=15
        )

        # 🟢 Log response
        print("\n--- 🟢 Response Received ---------------------------")
        print(f"🔸 STATUS:  {resp.status_code}")
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" in content_type or "text" in content_type:
            print(f"🔸 BODY PREVIEW:\n{resp.text[:1000]}")

        # Strip hop-by-hop headers
        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection']
        response_headers = {
            k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers
        }

        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except Exception as e:
        print("\n❌ Proxy Error:")
        print(str(e))
        return f"Proxy error: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Proxy running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port)
