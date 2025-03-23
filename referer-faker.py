from flask import Flask, Response, request
import requests
import os
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

# Config
TARGET_URL = "https://fc9ae48bc0a4-search-app.gaitspace.net"
FAKE_REFERER = "https://stmarketing.isracard.co.il"

def rewrite_html(html: str, base_url: str) -> str:
    """Convert all relative paths to absolute paths based on base_url."""
    soup = BeautifulSoup(html, "html.parser")
    
    for tag in soup.find_all(["script", "link", "img", "iframe", "source"]):
        attr = "src" if tag.name != "link" else "href"
        if tag.has_attr(attr):
            src = tag[attr]
            if src.startswith("/"):
                tag[attr] = base_url + src
            elif src.startswith("//"):
                tag[attr] = "https:" + src
    return str(soup)

@app.route('/')
def proxy():
    headers = {
        'Referer': FAKE_REFERER,
        'User-Agent': request.headers.get('User-Agent')
    }

    try:
        resp = requests.get(TARGET_URL, headers=headers)
        content_type = resp.headers.get('Content-Type', '')

        # Rewrite HTML only if the response is text/html
        if 'text/html' in content_type:
            rewritten = rewrite_html(resp.text, TARGET_URL)
            return Response(rewritten, status=resp.status_code, content_type=content_type)
        else:
            # Stream other content types as-is
            return Response(resp.content, status=resp.status_code, content_type=content_type)
    except Exception as e:
        return f"Proxy error: {e}", 500

# Run with correct port on Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
