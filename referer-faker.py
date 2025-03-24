from flask import Flask, Response, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)  # ✅ Enable CORS for cross-origin POSTs

# Gaitspace backend
TARGET_BASE = "https://fc9ae48bc0a4-search-app.gaitspace.net"
FAKE_REFERER = "https://stmarketing.isracard.co.il"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def full_proxy(path):
    # Construct full target URL
    target_url = f"{TARGET_BASE}/{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"

    # Build headers with spoofed Referer
    headers = {
        'Referer': FAKE_REFERER,
        'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
        'Accept': request.headers.get('Accept', '*/*'),
        'Content-Type': request.headers.get('Content-Type', ''),
        'Origin': FAKE_REFERER  # Spoof Origin if required by backend
    }

    method = request.method.lower()
    req_func = getattr(requests, method)

    try:
        print(f"\n🔵 [{request.method}] /{path}")
        print(f"➡️ Forwarding to: {target_url}")
        if request.data:
            print(f"📦 Request Body: {request.get_data(as_text=True)}")

        resp = req_func(
            target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True,
            timeout=10
        )

        print(f"✅ Response Status: {resp.status_code}")
        if 'application/json' in resp.headers.get('Content-Type', ''):
            print(f"📨 Response Body: {resp.text[:500]}")  # Preview up to 500 chars

        # Remove hop-by-hop headers
        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection']
        response_headers = {
            k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers
        }

        return Response(resp.content, status=resp.status_code, headers=response_headers)

    except Exception as e:
        print(f"❌ Proxy Error: {e}")
        return f"Proxy error: {e}", 500

# Run on correct port for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Proxy running on port {port}")
    app.run(host='0.0.0.0', port=port)
