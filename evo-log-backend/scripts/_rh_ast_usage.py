"""Qui touche quel attribut de quel modele RH, exactement.

La reconciliation modele<->base ne peut pas se faire au grep simple : le meme mot
('heures_sup', 'nom_fichier') designe des colonnes de tables differentes. On
reconstruit donc le graphe nom -> modele pour chaque affectation
(`conge = Conge(...)`, `db.query(Conge)`, `c: Conge`) et on releve les attribus
lus/ecrits sur ces noms, fonction par fonction, plus les kwargs des
constructeurs.

Usage: python scripts/_rh_ast_usage.py [Conge Salaire ...]
Sortie: _rh_ast.json + resume console
"""
import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODELES = [
    "Conge", "Absence", "TempsTravail", "Formation", "ParticipationFormation",
    "EvaluationPerformance", "ContratTravail", "Salaire", "Prime",
    "DocumentEmploye", "Organigramme", "Competence", "CompetenceEmploye",
]

fichier = ROOT / "app" / "services" / "rh_service.py"
cible = sorted(Path("app").rglob("*.py"), key=str)

res = {m: {"constructeur": defaultdict(int), "attributs": defaultdict(int),
           "classes": defaultdict(int)} for m in MODELES}

def _modele_de(node):
    """Renvoie les modeles RH mentions dans une expression d'affectation.

    Couvre `conge = Conge(...)`, `conges = db.query(Conge).all()`,
    `dernier = req.first()` -- dans ce dernier cas on remonte l'expression
    complete, `db.query(Conge)` etant souvent sur une ligne precedente : on se
    limite a ce qui est visible dans la meme expression, le reste étant rattrape
    par les acces sur la classe.
    """
    trouves = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and sub.id in MODELES:
            trouves.append(sub.id)
    return trouves


for p in cible:
    if "models" in p.parts:
        continue
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        continue
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            continue
        liens = defaultdict(list)   # nom variable -> modele
        for node in ast.walk(fn):
            # conge = Conge(...)  /  conge = db.query(Conge)...
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                t = node.targets[0]
                if isinstance(t, ast.Name):
                    liens[t.id].extend(_modele_de(node.value))
            # Conge.statut == ...  (acces classe)
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                    and node.value.id in MODELES:
                res[node.value.id]["classes"][node.attr] += 1
            # Conge(employe_id=..., motif=...)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in MODELES:
                for kw in node.keywords:
                    if kw.arg:
                        res[node.func.id]["constructeur"][kw.arg] += 1
        # conge.statut / .statut = ... sur une variable liee
        for node in ast.walk(fn):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                for m in liens.get(node.value.id, ()):
                    res[m]["attributs"][node.attr] += 1

out = {m: {k: dict(v) for k, v in d.items()} for m, d in res.items()}
(ROOT / "_rh_ast.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

voulu = sys.argv[1:] or MODELES
for m in voulu:
    d = out[m]
    print("=== %s" % m)
    for section in ("attributs", "constructeur", "classes"):
        items = sorted(d[section].items(), key=lambda x: -x[1])
        if items:
            print("   %-12s : %s" % (section, " ".join("%s(%d)" % kv for kv in items)))
