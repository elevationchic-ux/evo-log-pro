"""Quick check: list 404_reel gaps from the audit report."""
import json, pathlib
d = json.loads(pathlib.Path("_gap_report.json").read_text(encoding="utf-8"))
for g in d:
    if g["genre"] == "404_reel":
        print(f"  {g['appel']:50s}  {g['fichier']}:{g['ligne']}")
