# -*- coding: utf-8 -*-
"""Batch 23 : convertir /api/v1/acconage-avance de get_current_user -> require_perm.

Meme discipline que les batches 21/22 : table (methode + chemin) -> code
EXPLICITE ; toute route sans mapping ou tout mapping sans route fait echouer le
script. Aucun code par defaut ; chaque code est revu ensuite contre le
catalogue (scratch_check_perm_codes.py) et contre les roles (tests).
"""
import io
import re
import sys

TARGET = "app/routers/v1/acconage_avance.py"

MAPPING = {
    # Navires : registre propre (sous-module dedie batch 23) — un navire n'est
    # pas une escale.
    ("post", "/navires"): "acconage.navire.create",
    ("get", "/navires"): "acconage.navire.read",
    ("get", "/navires/{navire_id}"): "acconage.navire.read",
    # Escales : lecture/creation/modification ; le rapport d'escale est une
    # lecture des donnees de l'escale (pas un export comptable).
    ("get", "/escales"): "acconage.escale.read",
    ("post", "/escales"): "acconage.escale.create",
    ("put", "/escales/{escale_id}"): "acconage.escale.modify",
    ("get", "/escales/{escale_id}/rapport"): "acconage.escale.read",
    # Stowage : preparer = create/modify ; VALIDER un plan d'arrimage est un
    # acte d'approbation (secure loading) -> approve, chef uniquement.
    ("post", "/stowage-plans"): "acconage.stowage.create",
    ("post", "/stowage-plans/{plan_id}/positions"): "acconage.stowage.modify",
    ("put", "/stowage-plans/{plan_id}/valider"): "acconage.stowage.approve",
    # Moyens du terminal (grues, remorqueurs) : registre = moyen.* ; la
    # reservation d'une grue est son propre objet -> reservation.create.
    # Disponibilite = lecture des moyens.
    ("post", "/grues"): "acconage.moyen.create",
    ("put", "/grues/{grue_id}"): "acconage.moyen.modify",
    ("post", "/grues/reservations"): "acconage.reservation.create",
    ("get", "/grues/disponibles"): "acconage.moyen.read",
    ("post", "/remorqueurs"): "acconage.moyen.create",
    ("put", "/remorqueurs/{remorqueur_id}"): "acconage.moyen.modify",
    # Amarage : jalon operationnel de l'escale (le document n'a pas de vie
    # propre ici) -> escale.modify, pas un nouveau sous-module.
    ("post", "/amarages"): "acconage.escale.modify",
    # Conteneurs : enregistrement et inspection phytosanitaire (maj du
    # statut du conteneur).
    ("post", "/conteneurs"): "acconage.conteneur.create",
    ("put", "/conteneurs/{conteneur_id}/inspection-phytosanitaire"): "acconage.conteneur.modify",
    # Connaissements (B/L) : emission = acte porteur de responsabilite
    # documentaire ; les roles operationnels ne l'ont pas (voir tests).
    ("post", "/connaissements"): "acconage.connaissement.create",
    ("put", "/connaissements/{bl_id}"): "acconage.connaissement.modify",
    ("post", "/packing-lists"): "acconage.packing_list.create",
    # Manifestes : sous-module existant ; les marchandises dangereuses
    # modifient le manifeste (pas un objet separe).
    ("get", "/manifestes"): "acconage.manifeste.read",
    ("post", "/manifestes"): "acconage.manifeste.create",
    ("post", "/manifestes/{manifeste_id}/marchandises-dangereuses"): "acconage.manifeste.modify",
    ("put", "/manifestes/{manifeste_id}"): "acconage.manifeste.modify",
    # Frais portuaires (surestaries + THC) : un calcul qui cree une ligne de
    # frais = create ; contester/modifier = modify (acte du chef en pratique,
    # voir roles) ; lecture des surestaries en cours = read.
    ("post", "/surestaries"): "acconage.frais.create",
    ("get", "/escales/{escale_id}/surestaries"): "acconage.frais.read",
    ("put", "/surestaries/{surestarie_id}"): "acconage.frais.modify",
    ("post", "/thc"): "acconage.frais.create",
    ("put", "/thc/{thc_id}"): "acconage.frais.modify",
    # Nettoyage de cales : objet a cycle propre (enregistrer -> completer).
    ("post", "/nettoyage-cales"): "acconage.nettoyage.create",
    ("put", "/nettoyage-cales/{nettoyage_id}"): "acconage.nettoyage.modify",
    # Dockers temporaires : affectation/lecture/modif/retrait = CRUD
    # d'execution ; CLOTURER la liste de l'escale (paie engagee) = approve.
    ("post", "/escales/{escale_id}/dockers-temporaires"): "acconage.dockers.create",
    ("get", "/escales/{escale_id}/dockers-temporaires"): "acconage.dockers.read",
    ("put", "/dockers-temporaires/{docker_id}"): "acconage.dockers.modify",
    ("delete", "/dockers-temporaires/{docker_id}"): "acconage.dockers.delete",
    ("post", "/escales/{escale_id}/cloture-dockers"): "acconage.dockers.approve",
}

DECORATOR = re.compile(r'@router\.(get|post|put|patch|delete)\("([^"]+)"')
DEP_LINE = re.compile(r'^(\s*)current_user: User = Depends\(get_current_user\)(\s*,?\s*)$')

with io.open(TARGET, encoding="utf-8") as fh:
    lines = fh.read().splitlines(keepends=True)

out, current, used, missing = [], None, set(), []
seen_routes = set()
for line in lines:
    m = DECORATOR.search(line)
    if m:
        key = (m.group(1), m.group(2))
        seen_routes.add(key)
        current = MAPPING.get(key)
        if current is None:
            missing.append(key)
    d = DEP_LINE.match(line.rstrip("\n"))
    if d and current:
        line = '%scurrent_user: User = Depends(require_perm("%s"))%s\n' % (d.group(1), current, d.group(2))
        used.add(current)
        current = None
    out.append(line)

unreached = {k for k in MAPPING if k not in seen_routes}
if missing or unreached:
    print("ROUTES SANS MAPPING:", missing)
    print("MAPPING SANS ROUTE:", unreached)
    sys.exit(1)

text = "".join(out)
leftovers = [i + 1 for i, l in enumerate(out) if "Depends(get_current_user)" in l]
if leftovers:
    print("RESTES get_current_user lignes:", leftovers)
    sys.exit(1)

if "from app.core.permissions import require_perm" not in text:
    text = text.replace(
        "from app.core.security import get_current_user\n",
        "from app.core.permissions import require_perm\n",
    )

with io.open(TARGET, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text)

print("OK: %d routes converties, %d codes distincts" % (len(seen_routes), len(used)))
