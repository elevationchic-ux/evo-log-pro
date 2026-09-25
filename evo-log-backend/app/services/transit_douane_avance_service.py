"""Transit & Douane Avancé Service - DUM SYDONIA, Guichet Unique GUCE, Taxation TEC CEMAC"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.not_implemented import not_implemented


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
            regime=regime,
            db=db,
        )
        return {
            "numero_dum": numero_dum,
            "regime": regime,
            "code_sh": code_sh,
            "pays_origine": pays_origine,
            "valeur_cif_xaf": valeur_cif_xaf,
            "taxation": taxation,
            "statut": "PREPAREE_LOCALEMENT",  # jamais transmise à SYDONIA : voir GuichetUniqueService
            "date_depot": datetime.now().isoformat()
        }


class GuichetUniqueService:
    """Service d'intégration avec le Guichet Unique des Opérations du Commerce Extérieur (GUCE Cameroun)"""
    
    @staticmethod
    def teletransmettre_guce(numero_dum: str, donnees_declaration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Télétransmission GUCE e-GUCE.

        Renvoie désormais un 501 explicite : l'ancien code fabriquait une
        référence « GUCE-DLA-... » et un statut « ACQUITTE_ELECTRONIQUE »
        sans aucun échange avec le Guichet Unique  un acte réglementaire.
        """
        not_implemented(
            "Télétransmission GUCE e-GUCE",
            "connecteur officiel GUCE (compte opérateur, schéma de message "
            "e-Cameroun, accusés signés). Aucun acquit n'est émis sans dépôt réel.",
        )


class TaxationDouaniereService:
    """Calculateur des Droits et Taxes de Douane selon le Tarif Extérieur Commun (TEC CEMAC).

    Delegate vers le moteur UNIQUE ``app.services.taxation_douaniere`` : la formule
    n'est plus codee en dur ici (l'ancien code ignorait completement ``code_sh`` et
    appliquait 20% a tout, d'ou des montants divergents d'un ecran a l'autre).
    """

    @staticmethod
    def calculer_droits_et_taxes(
        valeur_cif_xaf: float,
        code_sh: str,
        regime: str = "IM4",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        from app.services.taxation_douaniere import calculer_liquidation

        return calculer_liquidation(
            valeur_en_douane=valeur_cif_xaf,
            db=db,
            code_sh=code_sh,
            regime=regime,
            # Quand la position SH est absente de la nomenclature (tables non
            # importees, cf. P1 #1), on retombe sur le taux "produit fini" 20%
            # MAIS le resultat est alors marque simulation=True / source_taux.
            defaut_dd_simulation=0.20,
        )
