"""Moteur UNIQUE de liquidation douaniere CEMAC / Cameroun (source de verite).

Historique du probleme (P1 #2) : cinq sites calculaient separement les droits
et taxes d'un meme conteneur, avec des formules divergentes :

  • base TVA tantot (valeur seule), tantot (valeur + DD), tantot
    (valeur + DD + redevance + CCI)  -> un TVA different selon l'ecran ;
  • taux exprimes en fraction (0.20) ici, en pourcentage (20.0) la ;
  • composantes incoherentes : CCI a 1% pour l'un, 0.4% pour l'autre,
    redevance 0.45% ou forfait fixe 15 000, prelevement OHADA present ou absent ;
  • droits "codés en dur" (20%) ignores de la position SH reellement saisie.

Ce module centralise LA formule. Tous les endpoints deleguent ici afin qu'un
evenement donne livre TOUJOURS le meme montant, quel que soit l'ecran.

Regle retenue (a confirmer avec le tarif officiel CEMAC en vigueur, cf. P1 #1 :
les tables de nomenclature sont encore vides tant que le tarif n'est pas importe) :

  Droit de Douane (DD)  = assiette * taux_dd(position SH)
  Redevance informatique= assiette * 0.45 %
  CCI communautaire     = assiette * 1 %
  Prelevement OHADA     = assiette * 0.05 %
  Base TVA              = assiette + DD + redevance + CCI
  TVA                   = base TVA * 19.25 %
  Precompte IS          = assiette * 2.2 %
  Total a liquider      = DD + redevance + CCI + OHADA + TVA + precompte

Le taux_dd est resolu dans cet ordre (jamais inventé silencieusement) :
  1. nomenclature CEMAC en base (position SH active)   -> source "nomenclature_cemac"
  2. taux explicitement fourni par l'appelant           -> source "manuel"
  3. categorie TEC demandee                             -> source "categorie_tec"
  4. defaut de simulation fourni par l'appelant         -> source "defaut_simulation"
  Sinon : ValueError (le routeur repond 400) : on ne facture pas un taux fantome.

Toute liquidation est marquee ``simulation=True`` : ce n'est jamais un acte
reglementaire, seul le visuel DGI/SYDONIA fait foi.
"""
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

# --- Parametres fiscaux centralises (Cameroun / CEMAC) ---------------------
TAUX_TVA_CMR = 0.1925                 # TVA 19,25 % (hors centimes additionnels)
TAUX_REDEVANCE_INFORMATIQUE = 0.0045  # RID / redevance informatique douaniere
TAUX_CCI_COMMUNAUTAIRE = 0.01         # Contribution Communautaire d'Integration
TAUX_PRELEVEMENT_OHADA = 0.0005       # Prelevement communautaire OHADA
TAUX_PRECOMPTE_IS = 0.022             # Precompte sur achats (IS) importateur

# Tarif Extérieur Commun : categorie TEC -> taux DD (fraction).
# A CONFIRMER avec le tarif officiel en vigueur (P1 #1).
TEC_CATEGORIES: Dict[int, float] = {0: 0.00, 1: 0.05, 2: 0.10, 3: 0.20}

# Origines beneficiaires d'une exoneration du droit de douane.
ORIGINES_EXONEREES = {"CEMAC", "ZLECAF", "UEAC"}


def _round(value: float) -> float:
    return round(value, 2)


def _normaliser_taux(taux: float) -> float:
    """Accepte un taux en pourcentage (20.0) ou en fraction (0.20).

    Un taux 'de douane' ne depasse jamais 100 % ; toute valeur superieure a 1
    est donc un pourcentage a ramener a la fraction.
    """
    return taux / 100.0 if taux > 1 else taux


def resoudre_taux_dd(
    db: Optional[Session],
    code_sh: Optional[str],
    taux_dd_explicite: Optional[float],
    categorie_tec: Optional[int],
    defaut_dd_simulation: Optional[float],
) -> tuple[float, str, bool]:
    """Retourne (taux_dd_fraction, source_taux, simulation).

    Lever ValueError si aucun taux ne peut etre resolu honnetement.
    """
    if db is not None and code_sh:
        from app.models.transit_avance import NomenclatureCEMAC

        entree = db.query(NomenclatureCEMAC).filter(
            NomenclatureCEMAC.code_hs == code_sh,
            NomenclatureCEMAC.statut == "actif",
        ).first()
        if entree is not None and entree.taux_dd is not None:
            return _normaliser_taux(float(entree.taux_dd)), "nomenclature_cemac", False

    if taux_dd_explicite is not None:
        return _normaliser_taux(float(taux_dd_explicite)), "manuel", False

    if categorie_tec is not None:
        if int(categorie_tec) not in TEC_CATEGORIES:
            raise ValueError(
                f"Categorie TEC inconnue : {categorie_tec} "
                f"(attendu 0..3)."
            )
        return TEC_CATEGORIES[int(categorie_tec)], "categorie_tec", True

    if defaut_dd_simulation is not None:
        return _normaliser_taux(float(defaut_dd_simulation)), "defaut_simulation", True

    raise ValueError(
        "Impossible de determiner le droit de douane : position SH absente de la "
        "nomenclature CEMAC et aucun taux/categorie fourni. Importer le tarif "
        "officiel ou saisir le taux explicitement."
    )


def calculer_liquidation(
    *,
    valeur_en_douane: float,
    db: Optional[Session] = None,
    code_sh: Optional[str] = None,
    taux_dd_explicite: Optional[float] = None,
    taux_tva_explicite: Optional[float] = None,
    categorie_tec: Optional[int] = None,
    defaut_dd_simulation: Optional[float] = None,
    origine: str = "HORS_ZONE",
    regime: str = "IM4",
    avec_precompte_is: bool = True,
) -> Dict[str, Any]:
    """Liquidation unique et deterministe des droits et taxes en douane.

    ``valeur_en_douane`` : assiette CAF/CIF en XAF.
    Voir le docstring du module pour la formule et l'ordre de resolution.
    """
    if valeur_en_douane is None or valeur_en_douane < 0:
        raise ValueError("La valeur en douane doit etre un montant XAF positif.")

    assiette = float(valeur_en_douane)

    taux_dd, source_taux, simulation = resoudre_taux_dd(
        db, code_sh, taux_dd_explicite, categorie_tec, defaut_dd_simulation
    )

    if taux_tva_explicite is not None:
        taux_tva = _normaliser_taux(float(taux_tva_explicite))
    else:
        taux_tva = TAUX_TVA_CMR

    # Régime : seule la mise a la consommation (IM4) liquide DD + TVA.
    en_mise_en_consommation = (regime or "IM4").upper() == "IM4"
    # Origine : CEMAC / ZLECAF -> droit de douane exonere (TVA et redevances dus).
    exonere_origine = (origine or "").upper() in ORIGINES_EXONEREES

    taux_dd_applique = 0.0 if (exonere_origine or not en_mise_en_consommation) else taux_dd
    if exonere_origine:
        source_taux = "exoneration_origine"

    droit_douane = assiette * taux_dd_applique
    redevance_info = assiette * TAUX_REDEVANCE_INFORMATIQUE
    cci_cemac = assiette * TAUX_CCI_COMMUNAUTAIRE
    prelevement_ohada = assiette * TAUX_PRELEVEMENT_OHADA

    base_tva = assiette + droit_douane + redevance_info + cci_cemac
    tva = base_tva * taux_tva if en_mise_en_consommation else 0.0
    precompte_is = assiette * TAUX_PRECOMPTE_IS if (avec_precompte_is and en_mise_en_consommation) else 0.0

    total = droit_douane + redevance_info + cci_cemac + prelevement_ohada + tva + precompte_is

    return {
        "valeur_en_douane_xaf": _round(assiette),
        # Cles alias conservees pour les consommateurs existants.
        "valeur_cif_xaf": _round(assiette),
        "valeur_caf_xaf": _round(assiette),
        "taux_dd": taux_dd_applique,
        "taux_tva": taux_tva,
        "droit_douane_dd": _round(droit_douane),
        "redevance_informatique": _round(redevance_info),
        "cci_cemac": _round(cci_cemac),
        "prelevement_ohada": _round(prelevement_ohada),
        "base_tva": _round(base_tva),
        "tva_1925": _round(tva),
        "precompte_is": _round(precompte_is),
        "total_a_liquider_xaf": _round(total),
        "devise": "XAF",
        "regime": regime,
        "origine": origine,
        "source_taux": source_taux,
        "simulation": bool(simulation or source_taux != "nomenclature_cemac"),
        "note": (
            "Estimation basee sur la formule centralisee CEMAC. Les taux definitifs "
            "dependent du tarif officiel en vigueur et du visuel DGI/SYDONIA."
        ),
    }
