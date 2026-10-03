# -*- coding: utf-8 -*-
"""Batch 24 : convertir /api/v1/qhse de get_current_user -> require_perm.

Meme discipline que les batches 21/22/23 : table (methode + chemin) -> code
EXPLICITE ; toute route sans mapping ou tout mapping sans route fait echouer le
script. 41 routes : les 38 auth-seules de l'inventaire + les 3 ex-publiques
recouvertes par les corrections d'honnetete (permis-travail, imdg/segregation,
csst-cnps/bilan) qui portent desormais une dependance d'authentification.
Aucun code par defaut ; chaque code est revu ensuite contre le catalogue
(scratch_check_perm_codes.py) et contre les roles (tests).
"""
import io
import re
import sys

TARGET = "app/routers/v1/qhse.py"

MAPPING = {
    # Analyses de risque : l'evaluation d'un danger est un objet propre. Pas
    # de lecture exposee ici (les listings passent par les registres metier).
    ("post", "/analyses-risques"): "qhse.risque.create",
    ("put", "/analyses-risques/{analyse_id}"): "qhse.risque.modify",
    # Actions de prevention issues des analyses.
    ("post", "/actions-prevention"): "qhse.prevention.create",
    ("put", "/actions-prevention/{action_id}"): "qhse.prevention.modify",
    # Plans de prevention : meme domaine que les actions (plan d'ensemble).
    ("post", "/plans-prevention"): "qhse.prevention.create",
    ("put", "/plans-prevention/{plan_id}"): "qhse.prevention.modify",
    # EPI requis par poste/zone.
    ("post", "/epi-requis"): "qhse.epi.create",
    ("put", "/epi-requis/{epi_id}"): "qhse.epi.modify",
    # Accidents du travail : DECLARER est deja un acte complet (c'est le
    # signalement lui-meme, pas un brouillon a faire valider) -> create.
    ("get", "/accidents"): "qhse.accident.read",
    ("post", "/accidents"): "qhse.accident.create",
    ("put", "/accidents/{accident_id}"): "qhse.accident.modify",
    # Investigations : menees par l'officier QHSE, objet propre.
    ("get", "/investigations"): "qhse.investigation.read",
    ("post", "/investigations"): "qhse.investigation.create",
    ("put", "/investigations/{investigation_id}"): "qhse.investigation.modify",
    # Certifications / normes (ISO 45001, 14001, ISPS) : registre des
    # exigences et de leur etat. L'audit de certification externe n'est pas
    # pronounce par l'appli -> pas d'approve expose.
    ("get", "/certifications"): "qhse.certification.read",
    ("post", "/certifications"): "qhse.certification.create",
    ("put", "/certifications/{certification_id}"): "qhse.certification.modify",
    # Audits internes : mener = creer ; clore/amender = modifier.
    ("get", "/audits"): "qhse.audit.read",
    ("post", "/audits"): "qhse.audit.create",
    ("put", "/audits/{audit_id}"): "qhse.audit.modify",
    # HACCP : le plan et ses points critiques (CCP) forment un seul objet
    # documentaire -> haccp.* ; l'enregistrement de controle quotidien est
    # l'execution mesuree -> controle.*.
    ("post", "/plans-haccp"): "qhse.haccp.create",
    ("put", "/plans-haccp/{plan_id}"): "qhse.haccp.modify",
    ("post", "/points-critiques"): "qhse.haccp.create",
    ("put", "/points-critiques/{ccp_id}"): "qhse.haccp.modify",
    ("post", "/enregistrements-haccp"): "qhse.controle.create",
    ("put", "/enregistrements-haccp/{enregistrement_id}"): "qhse.controle.modify",
    # Formations QHSE (habilitations, recyclages).
    ("get", "/formations"): "qhse.formation.read",
    ("post", "/formations"): "qhse.formation.create",
    ("put", "/formations/{formation_id}"): "qhse.formation.modify",
    # Indicateurs : la definition = create/modify ; la SAISIE d'une valeur
    # periodique est une modification de l'indicateur.
    ("post", "/indicateurs"): "qhse.indicateur.create",
    ("put", "/indicateurs/{indicateur_id}/valeur"): "qhse.indicateur.modify",
    ("put", "/indicateurs/{indicateur_id}"): "qhse.indicateur.modify",
    # Rapports : lecture seule des chiffres agreges (rapport securite annuel,
    # bilan CSST/CNPS tant qu'il sera 501, meme code d'intention).
    ("get", "/rapports/securite/{annee}"): "qhse.rapport.read",
    ("get", "/csst-cnps/bilan"): "qhse.rapport.read",
    # Registres generiques (gap_bridge) : fiches QHSE sans table dediee.
    ("get", "/"): "qhse.enregistrement.read",
    ("post", "/"): "qhse.enregistrement.create",
    ("get", "/{record_id}"): "qhse.enregistrement.read",
    ("put", "/{record_id}"): "qhse.enregistrement.modify",
    ("delete", "/{record_id}"): "qhse.enregistrement.delete",
    # Permis de travail : la route est desormais 501 (aucune signature
    # simulee) mais le code d'intention existe  celui qui pourra emettre un
    # permis reel le portera.
    ("post", "/permis-travail"): "qhse.permis.create",
    # Segregation IMDG : consultation de l'aide-memoire -> read.
    ("post", "/imdg/segregation"): "qhse.imdg.read",
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
