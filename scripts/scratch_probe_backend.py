import urllib.request, urllib.error, json
def call(path, method="GET", body=None, token=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token: headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request("http://127.0.0.1:8000" + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read().decode()[:400]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:
        return "ERR", str(e)[:400]

# Try common auth
for creds in [
    {"username":"admin@evolog.cm","password":"admin123"},
    {"username":"admin@kamlog.cm","password":"Admin.2024!"},
    {"email":"admin@evolog.cm","password":"admin123"},
    {"username":"superadmin@kamlog.cm","password":"Super.2024!"},
]:
    s, b = call("/api/v1/auth/login", method="POST", body=creds)
    print("login", creds.get("username") or creds.get("email"), "->", s, b[:150])
    if s == 200:
        tok = json.loads(b).get("access_token") or json.loads(b).get("token")
        print("token acquired")
        break
