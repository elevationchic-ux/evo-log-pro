# -*- coding: utf-8 -*-
"""Batch 22 : convertir /api/v1/finance de get_current_user -> require_perm.

Meme discipline que le batch 21 : table (methode + chemin) -> code EXPLICITE ;
toute route sans mapping ou tout mapping sans route fait echouer le script.
Aucun code par defaut invention ; chaque code est revu ensuite contre le
catalogue (scratch_check_perm_codes.py) et contre les roles (tests).
"""
import io
import re
import sys

TARGET = "app/routers/v1/finance.py"

MAPPING = {
    # Plan comptable SYSCOHADA : sous-module dedie (batch 22) — la creation
    # d'un compte n'est pas une ecriture de journal.
    ("get", "/plan-comptable"): "comptabilite.plan_comptable.read",
    ("post", "/plan-comptable"): "comptabilite.plan_comptable.create",
    ("put", "/plan-comptable/{compte_id}"): "comptabilite.plan_comptable.modify",
    # Ecritures : saisie = journal.create ; valider = journal.approve
    # (l'approbation comptable reste un acte distinct, jamais donne au
    #  comptable par defaut).
    ("post", "/ecritures"): "comptabilite.journal.create",
    ("put", "/ecritures/{ecriture_id}/valider"): "comptabilite.journal.approve",
    ("put", "/ecritures/{ecriture_id}"): "comptabilite.journal.modify",
    # Exercices : cloturer un exercice est un acte de validation -> approve.
    ("post", "/exercices"): "comptabilite.exercice.create",
    ("put", "/exercices/{exercice_id}/cloturer"): "comptabilite.exercice.approve",
    ("put", "/exercices/{exercice_id}"): "comptabilite.exercice.modify",
    # Facturation.
    ("post", "/factures"): "facturation.facture.create",
    ("post", "/factures/{facture_id}/lignes"): "facturation.facture.modify",
    ("put", "/factures/{facture_id}"): "facturation.facture.modify",
    ("get", "/factures/{facture_id}/pdf"): "facturation.facture.export",
    ("get", "/factures"): "facturation.facture.read",
    # Reglements / encaissements = mouvements de tresorerie.
    ("post", "/reglements"): "tresorerie.mouvement.create",
    ("put", "/reglements/{reglement_id}"): "tresorerie.mouvement.modify",
    ("get", "/encaissements"): "tresorerie.mouvement.read",
    ("post", "/encaissements"): "tresorerie.mouvement.create",
    # Declarations fiscales CEMAC : preparer = create/modify ; le depot
    # reel reste 501 (aucune integration GUCE) donc aucun approve n'est
    # expose ici — les endpoints maps sont des brouillons de declaration.
    ("post", "/tva-declarations"): "fiscalite.declarations.create",
    ("put", "/tva-declarations/{declaration_id}"): "fiscalite.declarations.modify",
    ("post", "/retenues-source"): "fiscalite.declarations.create",
    ("put", "/retenues-source/{retenue_id}"): "fiscalite.declarations.modify",
    ("post", "/is-declarations"): "fiscalite.declarations.create",
    ("put", "/is-declarations/{declaration_id}"): "fiscalite.declarations.modify",
    ("post", "/centimes-additionnels"): "fiscalite.declarations.create",
    ("put", "/centimes-additionnels/{centimes_id}"): "fiscalite.declarations.modify",
    ("post", "/patentes"): "fiscalite.declarations.create",
    ("put", "/patentes/{patente_id}"): "fiscalite.declarations.modify",
    ("get", "/exercices/{exercice_id}/rapport-fiscal"): "fiscalite.declarations.read",
    # Etats de synthese : creer/modifier un bilan ou un CR n'est pas
    # l'approuver (bilan.approve reste reserve aux etats validates).
    ("post", "/bilans"): "comptabilite.bilan.create",
    ("put", "/bilans/{bilan_id}"): "comptabilite.bilan.modify",
    ("post", "/comptes-resultat"): "comptabilite.compte_resultat.create",
    ("put", "/comptes-resultat/{compte_id}"): "comptabilite.compte_resultat.modify",
    # Signature electronique d'une facture = acte d'approbation de la facture.
    ("post", "/signatures-electroniques"): "facturation.facture.approve",
    ("put", "/signatures-electroniques/{signature_id}"): "facturation.facture.modify",
    # KPI et series : memes objets metier que le tableau de bord finance
    # (CA, impayes, recouvrement) -> lecture de factures. Convention alignee
    # sur celle de transport_avance (kpi -> read du domaine qui calcule).
    ("get", "/kpis"): "facturation.facture.read",
    ("get", "/analytics/chart-data"): "facturation.facture.read",
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
