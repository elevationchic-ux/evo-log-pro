"""Etat CI public (repo public, sans token) : 8 dernieres runs, etape en echec
et annotations ::error:: des runs test-backend en failure."""
import json
import time
import urllib.request

API = "https://api.github.com/repos/elevationchic-ux/evo-log-pro"
HDRS = {"User-Agent": "ci-probe", "Accept": "application/vnd.github+json"}


def get(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


runs = get(f"{API}/actions/runs?per_page=8")["workflow_runs"]
for run in runs:
    print(f"{run['id']} {run['head_sha'][:7]} {run['status']} {run['conclusion']} {run['created_at']}")
    if run["status"] == "completed" and run["conclusion"] == "failure":
        try:
            jobs = get(run["jobs_url"])["jobs"]
        except Exception as e:
            print("   jobs err", e)
            continue
        for job in jobs:
            if job["conclusion"] != "failure":
                continue
            print(f"   JOB {job['name']} -> failure")
            for st in job["steps"]:
                if st["conclusion"] == "failure":
                    print(f"     step FAILED: {st['name']}")
            try:
                anns = get(f"{API}/check-runs/{job['check_run_id']}/annotations")
                for a in anns[:6]:
                    msg = (a.get("message") or "").replace("\n", " | ")[:300]
                    print(f"     ANN[{a['level']}] {a.get('path')}:{a.get('start_line')} {msg}")
            except Exception as e:
                print("     ann err", e)
            break  # first failing job is enough
    time.sleep(0.4)
