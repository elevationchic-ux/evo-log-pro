import urllib.request, urllib.error, json
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=3) as r:
        print("backend up:", r.status, r.read().decode()[:200])
except Exception as e:
    print("backend DOWN:", type(e).__name__, e)
