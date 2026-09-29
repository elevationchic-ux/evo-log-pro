import urllib.request, time

for i in range(5):
    t = time.time()
    try:
        with urllib.request.urlopen(
            "https://evo-log-backend-production.up.railway.app/api/health",
            timeout=20,
        ) as r:
            print("health %d -> %s in %.1fs" % (i, r.status, time.time() - t))
    except Exception as e:
        code = getattr(e, "code", "")
        print("health %d -> ERR %s %s in %.1fs" % (i, type(e).__name__, code, time.time() - t))
    time.sleep(5)
