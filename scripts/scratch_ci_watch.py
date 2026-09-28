"""Surveille le run CI du dernier SHA pousse et rapporte les annotations."""
import io
import json
import os
import sys
import time
import urllib.request


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "curl"})
    return json.load(urllib.request.urlopen(req))


REPO = "https://api.github.com/repos/elevationchic-ux/evo-log-pro"
sha = sys.argv[1] if len(sys.argv) > 1 else None

runs = get(REPO + "/actions/runs?per_page=8")["workflow_runs"]
for x in runs[:8]:
    print(x["id"], x["head_sha"][:7], x["status"], x["conclusion"])

cand = [x for x in runs if sha and x["head_sha"].startswith(sha)]
if not cand and sha:
    cand = [x for x in runs if x["head_sha"][:7] == sha[:7]]
if not cand:
    cand = runs[:1]
d = cand[0]
rid = d["id"]
print("watching", rid, d["head_sha"][:7])
for _ in range(25):
    d = get("%s/actions/runs/%d" % (REPO, rid))
    if d["status"] == "completed":
        break
    time.sleep(60)
print("conclusion:", d["conclusion"])
jobs = get(d["jobs_url"])["jobs"]
for j in jobs:
    print(j["name"], "|", j["conclusion"])
tb = [j for j in jobs if j["name"] == "test-backend"][0]
for s in tb["steps"]:
    if s["conclusion"] not in ("success", None):
        print(" step:", s["name"], "->", s["conclusion"])
ann = get("%s/check-runs/%d/annotations" % (REPO, tb["id"]))
lines = []
for a in ann:
    if a["annotation_level"] in ("failure", "warning"):
        lines.append("ANN[%s]: %s" % (a["annotation_level"], a["message"][:1500]))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ci_watch_report.txt")
io.open(out, "w", encoding="utf-8").write("\n".join(lines))
for ln in lines:
    print(ln)
