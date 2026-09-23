"""Detecte les endpoints qui retournent un succes fabrique (aucun acces DB).

Un endpoint est considere 'faux succes' si son corps ne reference jamais la
session DB (db / SessionLocal / query / execute / get_db / .all() / .first()
/ .commit / await ...service...) ET retourne un literal (dict/list/f-string)
sans lever HTTPException 501. On signale aussi les 501 explicites.
"""
import ast
import pathlib

ROOT = pathlib.Path("app/routers")

DB_TOKENS = {
    "db", "SessionLocal", "query", "execute", "get_db", "scalar",
    "scalars", "commit", "rollback", "flush", "add", "delete", "merge",
    "service", "Service", "session", "await_",
}


def uses_db(fn: ast.AST) -> bool:
    src = ast.unparse(fn)
    if "db." in src or "db)" in src or " db" in src:
        return True
    for tok in ("SessionLocal", "get_db", ".query(", ".execute(", ".scalars(",
                ".add(", ".commit(", ".flush(", "Depends(get_db)", ".all()",
                ".first()", ".get(", "service.", "Service("):
        if tok in src:
            return True
    return False


def returns_literal(fn: ast.AST) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Return):
            v = node.value
            if isinstance(v, (ast.Dict, ast.List, ast.Constant, ast.JoinedStr)):
                return True
    return False


def raises_501(fn: ast.AST) -> bool:
    src = ast.unparse(fn)
    return "501" in src or "NOT_IMPLEMENTED" in src or "NotImplemented" in src


findings = {"fake": [], "stub501": [], "no_db_ok": []}
for path in sorted(ROOT.rglob("*.py")):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception as e:
        print("PARSE ERR", path, e)
        continue
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        deco = [ast.unparse(d) for d in node.decorator_list]
        is_route = any(d.startswith("router.") for d in deco)
        if not is_route:
            continue
        if raises_501(node):
            findings["stub501"].append(f"{path}:{node.name}")
        elif not uses_db(node) and returns_literal(node):
            findings["fake"].append(f"{path}:{node.name}")

print("=== FAUX SUCCES (retournent du fabrique, 0 DB) ===", len(findings["fake"]))
for f in findings["fake"]:
    print("  ", f)
print("=== 501 EXPLICITES ===", len(findings["stub501"]))
for f in findings["stub501"]:
    print("  ", f)
