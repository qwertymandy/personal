from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)

def get_mode_csp(mode):
    """Your existing CSP modes 0-3"""
    modes = {
        '0': '',  # No CSP
        '1': "default-src 'self'; script-src 'self'",
        '2': "default-src *; script-src *",  # Relaxed
        '3': "default-src 'self'; script-src 'self'; object-src 'none'"
    }
    return modes.get(mode, '')

@app.route('/')
def home():
    return """
    <h1>CSP Proxy v2</h1>
    <p><a href="/proxy/test?mode=4&url=http://testphp.vulnweb.com">Test Auto-CSP</a></p>
    <p><a href="/proxy/?mode=1&url=http://demo.testfire.net">Test Mode 1</a></p>
    """

@app.route('/proxy/')
@app.route('/proxy')
@app.route('/proxy/<path:path>')
def proxy(path=''):
    mode = request.args.get('mode', '0')
    target_url = request.args.get('url', 'http://testphp.vulnweb.com')
    
    print(f"Proxying '{path}' to {target_url} (mode={mode})")
    
    # Generate CSP
    if mode == '4':  # Auto mode - REAL crawler
        from crawl import crawl_sources
        from csp_generator import generate_csp
        sources = crawl_sources(target_url)
        csp_header = generate_csp(sources)
    else:
        csp_header = get_mode_csp(mode)
    
    try:
        resp = requests.get(
            urljoin(target_url, path), 
            params=request.args, 
            timeout=15  # Increased timeout
        )
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'Content-Security-Policy']
        headers = [(name, value) 
                  for (name, value) in resp.raw.headers.items()
                  if name.lower() not in excluded_headers]
        
        response = Response(resp.content, resp.status_code, headers)
        if csp_header:
            response.headers['Content-Security-Policy'] = csp_header
            print(f"✅ Injected CSP: {csp_header[:100]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ Proxy error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    print("🚀 Starting CSP Proxy v2 on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
