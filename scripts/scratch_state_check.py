# -*- coding: utf-8 -*-
"""Rapid state check: amenagement module surface (backend + frontend + migrations + tests)."""
import pathlib, re, json

root = pathlib.Path(__file__).resolve().parent.parent
be = root / "evo-log-backend"
fe = root / "evo-log-frontend" / "src"

print("== MODELES amenagement_portuaire ==")
txt = (be / "app/models/amenagement_portuaire.py").read_text(encoding="utf-8")
for m in re.finditer(r"class (\w+)\(Base\):\n\s+__tablename__ = \"([^\"]+)\"", txt):
    print(" ", m.group(1), "->", m.group(2))

print("\n== ENDPOINTS ==")
txt = (be / "app/routers/v1/amenagement_portuaire.py").read_text(encoding="utf-8")
eps = re.findall(r'@router\.(get|post|put|patch|delete)\(\s*"([^"]+)"', txt)
for meth, p in eps:
    print(f"  {meth.upper():6s} {p}")
print("  total:", len(eps))

print("\n== MIGRATIONS ==")
for f in sorted((be / "migrations/versions").glob("*.py")):
    print(" ", f.name)

print("\n== TESTS amenagement ==")
for f in (be / "tests").rglob("*amenag*"):
    print(" ", f.relative_to(be))

print("\n== FRONT amenagement-portuaire ==")
for f in sorted((fe / "app/(app)/amenagement-portuaire").rglob("*.tsx")):
    print(" ", f.relative_to(fe), f.stat().st_size, "o")

print("\n== FRONT lib api amenagement ==")
for f in fe.rglob("*.ts"):
    t = f.read_text(encoding="utf-8", errors="ignore")
    if "amenagement" in t.lower():
        print(" ", f.relative_to(fe))
