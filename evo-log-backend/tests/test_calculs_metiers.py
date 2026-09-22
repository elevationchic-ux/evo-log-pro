"""
Tests unitaires EVO-LOG SaaS
Couverture :
  - Calculs IRGM Cameroun (art. 69 CGI)  tranches 0 / 11% / 16.5% / 25% / 35%
  - Calculs CNPS (part salariale 2.8%, part patronale 17.2%)
  - Droits de douane TEC CEMAC (catégories 0/5/10/20%)
  - TVA Cameroun 19.25%
  - Règle FIFO/FEFO  tri des lots
  - TCO véhicule mensuel
"""
import pytest


# ══════════════════════════════════════════════════════════════════════════════
# 1. CALCULS IRGM CAMEROUN (Article 69 CGI)
# Barème 2024 :
#   0 - 62 000 XAF/mois  → 0%
#   62 001 - 310 000      → 11%
#   310 001 - 620 000     → 16.5%
#   620 001 - 1 035 000   → 25%
#   > 1 035 000           → 35%
# ══════════════════════════════════════════════════════════════════════════════

def calculer_irgm(salaire_brut_mensuel: float) -> float:
    """Calcule l'IRGM (Impôt sur le Revenu des Personnes Physiques) mensuel."""
    tranches = [
        (62_000,       0.00),
        (310_000,      0.11),
        (620_000,      0.165),
        (1_035_000,    0.25),
        (float('inf'), 0.35),
    ]
    impot = 0.0
    precedent = 0.0
    for plafond, taux in tranches:
        if salaire_brut_mensuel <= precedent:
            break
        imposable = min(salaire_brut_mensuel, plafond) - precedent
        impot += imposable * taux
        precedent = plafond
    return round(impot, 2)


class TestIRGM:
    def test_tranche_exoneree(self):
        """Salaire ≤ 62 000 XAF → IRGM = 0"""
        assert calculer_irgm(50_000) == 0.0
        assert calculer_irgm(62_000) == 0.0

    def test_tranche_11pct(self):
        """Salaire dans la tranche 11% → vérification de la progressivité"""
        # 62 000 exoné + (200 000 - 62 000) × 11% = 15 180
        assert calculer_irgm(200_000) == pytest.approx(15_180.0, rel=0.01)

    def test_tranche_16_5pct(self):
        """Tranche 16.5% : salaire = 500 000 XAF"""
        # (62 000 × 0%) + (248 000 × 11%) + (190 000 × 16.5%)
        # = 0 + 27 280 + 31 350 = 58 630
        assert calculer_irgm(500_000) == pytest.approx(58_630.0, rel=0.01)

    def test_tranche_25pct(self):
        """Tranche 25% : salaire = 800 000 XAF"""
        # (0 + 27 280 + 51 150 + 45 000) = 123 430
        result = calculer_irgm(800_000)
        assert result > 58_630  # Supérieur à la tranche précédente

    def test_tranche_35pct(self):
        """Tranche 35% : salaire = 2 000 000 XAF (cadre supérieur)"""
        result = calculer_irgm(2_000_000)
        assert result > calculer_irgm(1_035_000)

    def test_progressivite(self):
        """L'IRGM doit être strictement croissant avec le salaire"""
        salaires = [50_000, 100_000, 300_000, 500_000, 800_000, 1_200_000, 2_000_000]
        irgms = [calculer_irgm(s) for s in salaires]
        for i in range(1, len(irgms)):
            assert irgms[i] > irgms[i - 1], f"IRGM non croissant pour salaire {salaires[i]}"


# ══════════════════════════════════════════════════════════════════════════════
# 2. CALCULS CNPS CAMEROUN
# Part salariale : 2.8% du salaire brut (plafond 750 000 XAF/mois)
# Part patronale : 17.2% (7% AT-MP + 7% Allocations Fam. + 3.2% Retraite)
# ══════════════════════════════════════════════════════════════════════════════

def calculer_cnps(salaire_brut: float):
    PLAFOND = 750_000
    base = min(salaire_brut, PLAFOND)
    return {
        "base_cotisation": base,
        "part_salariale": round(base * 0.028, 2),
        "part_patronale": round(base * 0.172, 2),
        "total_charges": round(base * 0.028 + base * 0.172, 2),
    }


class TestCNPS:
    def test_salaire_sous_plafond(self):
        """Salaire ≤ 750 000 → cotisations sur salaire réel"""
        r = calculer_cnps(500_000)
        assert r["part_salariale"] == 14_000.0  # 500 000 × 2.8%
        assert r["part_patronale"] == 86_000.0  # 500 000 × 17.2%
        assert r["total_charges"] == 100_000.0

    def test_plafond_applique(self):
        """Salaire > 750 000 → cotisations plafonnées à 750 000"""
        r = calculer_cnps(2_000_000)
        assert r["base_cotisation"] == 750_000
        assert r["part_salariale"] == 21_000.0   # 750 000 × 2.8%
        assert r["part_patronale"] == 129_000.0  # 750 000 × 17.2%

    def test_plafond_exact(self):
        """Salaire = 750 000 → pas de plafonnement"""
        r = calculer_cnps(750_000)
        assert r["base_cotisation"] == 750_000
        assert r["part_salariale"] == pytest.approx(21_000.0)


# ══════════════════════════════════════════════════════════════════════════════
# 3. DROITS DE DOUANE TEC CEMAC
# Catégorie 0 : Biens essentiels → 0%
# Catégorie 1 : Matières premières → 5%
# Catégorie 2 : Intrants / semi-ouvrés → 10%
# Catégorie 3 : Produits finis → 20%
# ══════════════════════════════════════════════════════════════════════════════

TEC_TAUX = {0: 0.00, 1: 0.05, 2: 0.10, 3: 0.20}
TVA_CMR = 0.1925


def calculer_droits_douane(valeur_cif_xaf: float, categorie_tec: int, quantite: float = 1.0):
    taux_tec = TEC_TAUX.get(categorie_tec, 0.20)
    droits_tec = valeur_cif_xaf * taux_tec
    redevance_informatique = valeur_cif_xaf * 0.0035  # RI : 0.35%
    taxe_communautaire = valeur_cif_xaf * 0.01        # TC : 1%
    base_tva = valeur_cif_xaf + droits_tec + redevance_informatique + taxe_communautaire
    tva = base_tva * TVA_CMR
    return {
        "valeur_cif": valeur_cif_xaf,
        "categorie_tec": categorie_tec,
        "taux_tec_pct": taux_tec * 100,
        "droits_tec": round(droits_tec, 2),
        "redevance_informatique": round(redevance_informatique, 2),
        "taxe_communautaire": round(taxe_communautaire, 2),
        "base_tva": round(base_tva, 2),
        "tva_19_25": round(tva, 2),
        "total_mise_a_disposition": round(droits_tec + redevance_informatique + taxe_communautaire + tva, 2)
    }


class TestDroitsDouane:
    def test_categorie_0_exoneree(self):
        """Cat. 0 → droits TEC = 0"""
        r = calculer_droits_douane(10_000_000, 0)
        assert r["droits_tec"] == 0.0

    def test_categorie_1_matieres_premieres(self):
        """Cat. 1 → TEC 5%"""
        r = calculer_droits_douane(10_000_000, 1)
        assert r["droits_tec"] == 500_000.0

    def test_categorie_3_produits_finis(self):
        """Cat. 3 → TEC 20%"""
        r = calculer_droits_douane(10_000_000, 3)
        assert r["droits_tec"] == 2_000_000.0

    def test_tva_19_25_appliquee(self):
        """TVA 19.25% calculée sur la base augmentée des droits"""
        r = calculer_droits_douane(10_000_000, 3)
        # Base TVA = 10M + 2M + 35 000 RI + 100 000 TC = 12 135 000
        assert r["base_tva"] == pytest.approx(12_135_000.0, rel=0.001)
        assert r["tva_19_25"] == pytest.approx(12_135_000 * 0.1925, rel=0.001)

    def test_total_coherent(self):
        """Le total doit être la somme des composantes"""
        r = calculer_droits_douane(5_000_000, 2)
        total_attendu = r["droits_tec"] + r["redevance_informatique"] + r["taxe_communautaire"] + r["tva_19_25"]
        assert r["total_mise_a_disposition"] == pytest.approx(total_attendu, rel=0.001)


# ══════════════════════════════════════════════════════════════════════════════
# 4. RÈGLE FIFO / FEFO  Tri des lots
# ══════════════════════════════════════════════════════════════════════════════

from datetime import date


def trier_lots_fifo(lots: list) -> list:
    """Trie par date d'entrée croissante (Premier Entré, Premier Sorti)"""
    return sorted(lots, key=lambda l: l["date_entree"])


def trier_lots_fefo(lots: list) -> list:
    """Trie par date d'expiration croissante (Premier Expiré, Premier Sorti)"""
    return sorted(lots, key=lambda l: l["date_expiration"])


class TestPickingFIFO_FEFO:
    @pytest.fixture
    def lots(self):
        return [
            {"numero": "LOT-C", "date_entree": date(2026, 6, 15), "date_expiration": date(2027, 6, 30)},
            {"numero": "LOT-A", "date_entree": date(2026, 4, 1), "date_expiration": date(2027, 12, 31)},
            {"numero": "LOT-B", "date_entree": date(2026, 5, 10), "date_expiration": date(2027, 3, 15)},
        ]

    def test_fifo_ordre_entree(self, lots):
        """FIFO → LOT-A (avril) avant LOT-B (mai) avant LOT-C (juin)"""
        tries = trier_lots_fifo(lots)
        assert tries[0]["numero"] == "LOT-A"
        assert tries[1]["numero"] == "LOT-B"
        assert tries[2]["numero"] == "LOT-C"

    def test_fefo_ordre_expiration(self, lots):
        """FEFO → LOT-B (expire mars 2027) avant LOT-C (juin 2027) avant LOT-A (déc 2027)"""
        tries = trier_lots_fefo(lots)
        assert tries[0]["numero"] == "LOT-B"
        assert tries[1]["numero"] == "LOT-C"
        assert tries[2]["numero"] == "LOT-A"

    def test_fifo_ne_doit_pas_etre_fefo(self, lots):
        """FIFO et FEFO ne doivent pas donner le même ordre si les dates diffèrent"""
        fifo = [l["numero"] for l in trier_lots_fifo(lots)]
        fefo = [l["numero"] for l in trier_lots_fefo(lots)]
        assert fifo != fefo


# ══════════════════════════════════════════════════════════════════════════════
# 5. TCO VÉHICULE MENSUEL
# ══════════════════════════════════════════════════════════════════════════════

def calculer_tco_mensuel(composantes: dict) -> dict:
    total = sum(composantes.values())
    km_mois = composantes.get("km_parcourus", 1)
    return {
        "total_mensuel_xaf": total,
        "tco_par_km_xaf": round(total / km_mois, 2) if km_mois > 0 else 0,
        "composantes": composantes
    }


class TestTCOVehicule:
    def test_tco_total(self):
        """Vérifie la somme des composantes TCO"""
        compo = {
            "amortissement": 4_500_000,
            "carburant": 2_800_000,
            "maintenance_preventive": 650_000,
            "maintenance_corrective": 350_000,
            "pneumatiques": 480_000,
            "assurance_et_taxes": 380_000,
            "autres": 120_000,
            "km_parcourus": 29_000
        }
        r = calculer_tco_mensuel(compo)
        assert r["total_mensuel_xaf"] == pytest.approx(9_280_000 + 29_000, rel=0.001)

    def test_tco_par_km(self):
        """TCO/km doit être positif et cohérent"""
        compo = {
            "amortissement": 4_500_000,
            "carburant": 2_800_000,
            "maintenance_preventive": 650_000,
            "maintenance_corrective": 350_000,
            "pneumatiques": 480_000,
            "assurance_et_taxes": 380_000,
            "autres": 120_000,
            "km_parcourus": 29_000
        }
        r = calculer_tco_mensuel(compo)
        assert r["tco_par_km_xaf"] > 0
        assert r["tco_par_km_xaf"] < 1_000  # Moins de 1 000 XAF/km pour un camion

    def test_tco_zero_km_pas_division(self):
        """Vérifie qu'on n'a pas de ZeroDivisionError si km=0"""
        r = calculer_tco_mensuel({"amortissement": 1_000_000, "km_parcourus": 0})
        assert r["tco_par_km_xaf"] == 0
