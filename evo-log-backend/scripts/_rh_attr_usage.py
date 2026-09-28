"""Releve quels noms d'attributs le CODE utilise reellement pour les modeles RH.

Evite de deviner, dans la reconciliation modele<->base, quel nom est le bon :
un nom present en base et dans les services ne doit pas etre renomme par le
modele, et un nom que personne n'utilise ne merite pas de colonne.

Usage: python scripts/_rh_attr_usage.py
Sortie: _rh_attrs.json
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOMS = """
motif_refus commentaire_approbation commentaires_approbation pieces_jointes solde_conge
nom_fichier url_fichier chemin_fichier date_ajout date_emission date_expiration
justifie justifiee nombre_jours nombre_heures heure_debut heure_fin
heure_arrivee heure_depart heures_sup heures_supplementaires heures_travaillees
date_prime date_octroi periode niveau_maitrise niveau_requis
date_debut_poste date_fin_poste niveau_hierarchique sous_ordinates est_actif est_valide
numero_document organisme_emetteur date_validation validateur_id projet_id tache
certification_obtenue certificat_obtenu date_certificat certificat_valide_jusque note
objectifs_atteints objectifs_total commentaires note_globale date_evaluation
coefficient classification periode_essai periode_essai_jours
nombre_renouvellements date_dernier_renouvellement preavis motif_fin date_fin_reelle
convention_collective horaire_travail lieu_travail duree_jours duree_heures
nombre_places competences_visees type_formation fournisseur formateur agency_id
est_active date_enregistrement date_demande date_approbation approbateur_id
type_absence type_conge type_prime type_document type_contrat
salaire_base salaire_brut salaire_net devise statut motif date_debut date_fin
""".split()

FICHIERS = sorted((ROOT / "app").rglob("*.py"))
Ignore = {"app\\models\\rh.py"}

usage = defaultdict(lambda: defaultdict(int))
for p in FICHIERS:
    if any(k in str(p) for k in Ignore):
        continue
    texte = p.read_text(encoding="utf-8", errors="replace")
    for nom in NOMS:
        n = len(re.findall(r"\b%s\b" % re.escape(nom), texte))
        if n:
            usage[nom][str(p.relative_to(ROOT))] += n

out = {k: dict(v) for k, v in sorted(usage.items())}
(ROOT / "_rh_attrs.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("ecrit %s (%d noms)" % (ROOT / "_rh_attrs.json", len(out)))
