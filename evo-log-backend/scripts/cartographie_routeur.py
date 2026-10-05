"""Cartographie d'un routeur : methodes, permissions reellement exigees, 501.

Pourquoi ce script existe : la documentation du projet annonce des chiffres
(« 323 routes », « 22 routeurs ») que plus personne ne recounte, et un departement
comme l'amenagement portuaire melange volontairement des endpoints qui ecrivent
en base et des teleprocedures annoncees 501. Sans outil, la seule facon de
repondre a « qu'est-ce qui est vraiment branchable ? » etait de lire 1 200 lignes.

Le script ne devine rien : il import le routeur, lit ses routes declarees et
inspecte le source de chaque endpoint pour en tirer les codes `require_perm` et
les reponses `not_implemented`. La liste est donc celle du serveur, pas celle
d'un fichier markdown.

Usage :
    python scripts/cartographie_routeur.py amenagement_portuaire
    python scripts/cartographie_routeur.py --total          (tous les routeurs v1)
"""
import argparse
import importlib
import inspect
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

PERM_RE = re.compile(r'require_perm\(\s*"([a-z0-9_.]+)"')


def _details(endpoint):
    """Codes de permission exiges et statut 501, lies au source de l'endpoint."""
    try:
        source = inspect.getsource(endpoint)
    except OSError:  # fonction construite dynamiquement
        return set(), False
    return set(PERM_RE.findall(source)), "not_implemented(" in source


def decrire(module_nom):
    """(prefixe, endpoints) du routeur declare dans app/routers/v1/<module_nom>.py.

    Le nom de la variable n'est pas le meme d'un fichier a l'autre (`router`,
    `api_router`, ...) et certains fichiers n'exposent aucun routeur : on cherche
    les objets APIRouter dont les endpoints sont bien nes dans le module, sinon
    un `import` croise ferait croire a un routeur la ou il n'y en a pas.
    """
    from fastapi import APIRouter

    module = importlib.import_module(f"app.routers.v1.{module_nom}")
    routeurs = [v for v in vars(module).values() if isinstance(v, APIRouter)]
    prefixe = ""
    lignes = []
    for routeur in routeurs:
        for route in routeur.routes:
            if getattr(route.endpoint, "__module__", "") != module.__name__:
                continue
            for methode in sorted(m for m in route.methods if m != "HEAD"):
                codes, pour_501 = _details(route.endpoint)
                lignes.append({
                    "methode": methode,
                    "chemin": route.path,
                    "permissions": sorted(codes),
                    "501": pour_501,
                    "resume": (route.summary or "").strip(),
                })
        if not prefixe:
            prefixe = getattr(routeur, "prefix", "")
    return prefixe, lignes


def main():
    analyse = argparse.ArgumentParser(description=__doc__)
    analyse.add_argument("module", nargs="?", help="nom du fichier de app/routers/v1")
    analyse.add_argument("--total", action="store_true", help="compter les routes de chaque routeur v1")
    args = analyse.parse_args()

    dossier_v1 = RACINE / "app" / "routers" / "v1"
    if args.total:
        total_routes = 0
        silencieux = []
        for fichier in sorted(dossier_v1.glob("*.py")):
            if fichier.name == "__init__.py":
                continue
            try:
                prefix, lignes = decrire(fichier.stem)
            except Exception as exc:  # un fichier qui ne s'importe pas ne doit pas figer le bilan
                print(f"{fichier.name:<38} INIMPORTABLE ({type(exc).__name__}: {exc})")
                silencieux.append(fichier.name)
                continue
            total_routes += len(lignes)
            marque = "" if lignes else "  <- aucun endpoint declare"
            print(f"{fichier.name:<38} prefix={prefix or '-':<34} endpoints={len(lignes)}{marque}")
        print(f"\n{total_routes} endpoints declares par les routeurs v1.")
        if silencieux:
            print(f"{len(silencieux)} fichier(s) non importables : {', '.join(silencieux)}")
        return 0

    if not args.module:
        analyse.print_help()
        return 1

    prefix, lignes = decrire(args.module)
    print(f"Routeur {args.module} — prefixe {prefix or '(aucun)'}\n")
    for ligne in lignes:
        drapeau = "  [501 teleprocedure]" if ligne["501"] else ""
        perms = ", ".join(ligne["permissions"]) or "aucune permission declaree"
        print(f"{ligne['methode']:<6} {ligne['chemin']:<44} {perms}{drapeau}")
        if ligne["resume"]:
            print(f"       -> {ligne['resume']}")
    reels = sum(1 for x in lignes if not x["501"])
    print(f"\n{len(lignes)} endpoints : {reels} branchees en base, "
          f"{len(lignes) - reels} annonces 501.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
