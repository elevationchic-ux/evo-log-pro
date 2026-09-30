# -*- coding: utf-8 -*-
"""Batch 21 : convertir magasin_avance de get_current_user -> require_perm.

Script one-shot, idempotent (les lignes deja converties ne correspondent plus
au motif). Chaque route est mappee EXPLICITEMENT (methode + chemin) ; toute
route absente de la table fait echouer le script au lieu de passer en silence
(Zero-Mock : pas de protection « par defaut » inventee).
"""
import io
import re
import sys

TARGET = "app/routers/v1/magasin_avance.py"

# (METHODE, chemin decorator) -> code de permission du catalogue.
# Codes verifiables ensuite contre permission_catalog.iter_permission_rows().
MAPPING = {
    # Peremptions : lire la date limite est de la lecture de stock ; poser
    # une peremption est un evenement stock (mouvement).
    ("post", "/peremptions"): "magasin.mouvement.create",
    ("get", "/peremptions/fefo/{article_id}/{quantite}"): "magasin.stock.read",
    ("get", "/peremptions/critiques"): "magasin.stock.read",
    ("get", "/peremptions/expirees"): "magasin.stock.read",
    # Reservations : affecter/liberer de la marchandise = preparation (picking) ;
    # consommer materialise un mouvement reel.
    ("post", "/reservations"): "magasin.picking.create",
    ("put", "/reservations/{reservation_id}/liberer"): "magasin.picking.modify",
    ("put", "/reservations/{reservation_id}/consommer"): "magasin.mouvement.create",
    ("post", "/reservations/nettoyer"): "magasin.stock.modify",
    # Kits : nomenclature = preparation ; assembler consomme les composants.
    ("post", "/kits"): "magasin.picking.create",
    ("post", "/kits/{kit_id}/composants"): "magasin.picking.modify",
    ("post", "/kits/{kit_id}/assembler"): "magasin.mouvement.create",
    # Emplacements : plan du depot = donnee de stock.
    ("post", "/emplacements"): "magasin.stock.modify",
    ("get", "/emplacements/{emplacement_id}/stock"): "magasin.stock.read",
    # Transferts : un transfert EST un couple de mouvements.
    ("post", "/transferts"): "magasin.mouvement.create",
    ("put", "/transferts/{transfert_id}/executer"): "magasin.mouvement.create",
    # Inventaires : le sous-module inventaire existe, alignement direct.
    ("post", "/inventaires"): "magasin.inventaire.create",
    ("post", "/inventaires/{inventaire_id}/lignes"): "magasin.inventaire.modify",
    ("put", "/inventaires/{inventaire_id}/valider"): "magasin.inventaire.approve",
    ("get", "/inventaires/{inventaire_id}/precision"): "magasin.inventaire.read",
    # Referentiel fournisseur-stock = donnee de stock ; reauto est un acte
    # d'achat (le code existe deja dans le catalogue, domaine commerce).
    ("post", "/fournisseurs-stock"): "magasin.stock.modify",
    ("get", "/fournisseurs/{fournisseur_id}/performance"): "magasin.stock.read",
    ("post", "/reapprovisionnement/automatique/{fournisseur_id}"): "achats.commande.create",
    # Receptions : le sous-module achats.reception existe (ACTIONS completes).
    ("get", "/receptions"): "achats.reception.read",
    ("post", "/receptions"): "achats.reception.create",
    ("patch", "/receptions/{bon_id}"): "achats.reception.modify",
    ("post", "/receptions/{bon_id}/lignes"): "achats.reception.modify",
    ("put", "/receptions/{bon_id}/valider"): "achats.reception.approve",
    ("put", "/receptions/{bon_id}/refuser"): "achats.reception.approve",
    # Retours clients : declarer = mouvement ; traiter = decision (approve).
    ("get", "/retours"): "magasin.stock.read",
    ("post", "/retours"): "magasin.mouvement.create",
    ("patch", "/retours/{retour_id}"): "magasin.stock.modify",
    ("put", "/retours/{retour_id}/traiter"): "magasin.mouvement.approve",
    # Litiges transporteur : dossier ne du mouvement de stock/reception.
    ("get", "/litiges"): "magasin.mouvement.read",
    ("post", "/litiges"): "magasin.mouvement.create",
    ("patch", "/litiges/{litige_id}"): "magasin.mouvement.modify",
    ("put", "/litiges/{litige_id}/resoudre"): "magasin.mouvement.approve",
    # Colis : unites de preparation/expedition = picking.
    ("get", "/colis"): "magasin.picking.read",
    ("post", "/colis"): "magasin.picking.create",
    ("patch", "/colis/{colis_id}"): "magasin.picking.modify",
    ("put", "/colis/{colis_id}/etiqueter"): "magasin.picking.modify",
    ("put", "/colis/{colis_id}/palettiser"): "magasin.picking.modify",
    # KPI : extractions analytiques (export = sortir des chiffres hors systeme).
    ("get", "/kpi/rotation/{article_id}"): "magasin.mouvement.export",
    ("get", "/kpi/precision/{entrepot_id}"): "magasin.inventaire.read",
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
