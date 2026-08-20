import requests
from flask import Flask, request, make_response

app = Flask(__name__)


@app.route("/test")
def test():
    mode = request.args.get("mode", "0")

    html = f"""
    <!doctype html>
    <html>
    <head>
      <title>Hybrid CSP test</title>
    </head>
    <body>
      <h1>Hybrid CSP test page</h1>
      <p>Mode: {mode}</p>
      <script>
        alert("XSS test – mode {mode}");
      </script>
    </body>
    </html>
    """

    resp = make_response(html)

    if mode == "1":
        resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self';"
    elif mode == "2":
        resp.headers["Content-Security-Policy"] = "default-src *; script-src *;"
    elif mode == "3":
        resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none';"

    return resp


@app.route('/dvwa_xss/', methods=['GET', 'POST'])
@app.route('/dvwa_xss', methods=['GET', 'POST'])

    # ... rest of your code
def dvwa_xss():
    # 1. Read parameters from the proxy URL
    mode = request.args.get("mode", "0")   # we'll use this later for CSP
    name = request.args.get("name", "")   # this is the XSS payload

    # 2. Build the DVWA reflected-XSS URL
    dvwa_url = "http://127.0.0.1/dvwa/vulnerabilities/xss_r/index.php"
    # 3. Forward the GET request to DVWA, passing the 'name' parameter
    dvwa_resp = requests.get(
        dvwa_url,
        params={"name": name},
        cookies=request.cookies  # forwards your DVWA session cookie
    )

    # 4. Wrap DVWA's HTML in a Flask response
    resp = make_response(dvwa_resp.text)
    resp.status_code = dvwa_resp.status_code
    resp.headers["Content-Type"] = dvwa_resp.headers.get(
        "Content-Type", "text/html"
    )

    # 5. For THIS step, don't add any CSP yet.
    #    So mode is only "carried" but not used.

    return resp

if __name__ == "__main__":
    app.run(debug=True)
