"""Transit & Douane Avancé Service - DUM SYDONIA, Guichet Unique GUCE, Taxation TEC CEMAC"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session


class DUMService:
    """Service de gestion des Déclarations Uniques de Marchandises (DUM)"""
    
    @staticmethod
    def creer_dum(
        db: Session,
        regime: str,  # IM4, IM7, EX1, T1
        importateur_id: int,
        valeur_cif_xaf: float,
        code_sh: str,
        pays_origine: str = "FR"
    ) -> Dict[str, Any]:
        numero_dum = f"DUM-{date.today().year}-{regime}-{datetime.now().strftime('%m%d%H%M')}"
        taxation = TaxationDouaniereService.calculer_droits_et_taxes(
            valeur_cif_xaf=valeur_cif_xaf,
            code_sh=code_sh,
            regime=regime
        )
        return {
            "numero_dum": numero_dum,
            "regime": regime,
            "code_sh": code_sh,
            "pays_origine": pays_origine,
            "valeur_cif_xaf": valeur_cif_xaf,
            "taxation": taxation,
            "statut": "DEPOSEE_SYDONIA",
            "date_depot": datetime.now().isoformat()
        }


class GuichetUniqueService:
    """Service d'intégration avec le Guichet Unique des Opérations du Commerce Extérieur (GUCE Cameroun)"""
    
    @staticmethod
    def teletransmettre_guce(numero_dum: str, donnees_declaration: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "reference_guce": f"GUCE-DLA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "numero_dum": numero_dum,
            "statut_reception": "ACQUITTE_ELECTRONIQUE",
            "message": "Dossier validé par le Guichet Unique Portuaire de Douala",
            "date_acquit": datetime.now().isoformat()
        }


class TaxationDouaniereService:
    """Calculateur des Droits et Taxes de Douane selon le Tarif Extérieur Commun (TEC CEMAC)"""
    
    @staticmethod
    def calculer_droits_et_taxes(
        valeur_cif_xaf: float,
        code_sh: str,
        regime: str = "IM4"
    ) -> Dict[str, Any]:
        # Taux standard TEC CEMAC Catégorie 4 (Produits finis / Équipements)
        taux_dd = 0.20 if regime == "IM4" else 0.0  # Droit de Douane 20%
        droit_douane = valeur_cif_xaf * taux_dd
        
        # Redevance Informatique Douane (0.45%)
        redevance_info = valeur_cif_xaf * 0.0045
        
        # Contribution Communautaire d'Intégration CCI (1%)
        cci_cemac = valeur_cif_xaf * 0.01
        
        # Base TVA = Valeur CIF + Droit de Douane + Redevance Info + CCI
        base_tva = valeur_cif_xaf + droit_douane + redevance_info + cci_cemac
        
        # TVA Cameroun (19.25% incluant les centimes additionnels communaux CAC 10%)
        tva_1925 = base_tva * 0.1925 if regime == "IM4" else 0.0
        
        # Précompte sur achats IS (selon régime fiscal importateur: 2.2% à 5.5%)
        precompte_is = valeur_cif_xaf * 0.022 if regime == "IM4" else 0.0
        
        total_droits_taxes = droit_douane + redevance_info + cci_cemac + tva_1925 + precompte_is
        
        return {
            "valeur_cif_xaf": valeur_cif_xaf,
            "droit_douane_dd": droit_douane,
            "redevance_informatique": redevance_info,
            "cci_cemac": cci_cemac,
            "base_tva": base_tva,
            "tva_1925": tva_1925,
            "precompte_is": precompte_is,
            "total_a_liquider_xaf": total_droits_taxes,
            "devise": "XAF"
        }
