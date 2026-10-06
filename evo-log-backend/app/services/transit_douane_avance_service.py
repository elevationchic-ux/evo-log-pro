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
        Télétransmission GUCE e-GUCE via le connecteur officiel configure.

        - CUSTOMS_EDI_* configure  -> VERITABLE remise au guichet ; l'acquit
          retourne est celui du fournisseur, repondu par lui.
        - Non configure            -> 503 explicite. L'ancien code fabriquait
          une reference « GUCE-DLA-... » et un statut « ACQUITTE_ELECTRONIQUE »
          sans aucun echange : acte reglementaire, jamais simule desormais.
        """
        from app.utils.external import call_provider

        return call_provider(
            "CUSTOMS_EDI",
            "Teletransmission GUCE e-GUCE",
            path="/guce/teletransmission",
            payload={
                "numero_dum": numero_dum,
                "declaration": donnees_declaration,
            },
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
        origine: str = "HORS_ZONE",
        categorie_tec: Optional[int] = None,
        taux_dd_explicite: Optional[float] = None,
    ) -> Dict[str, Any]:
        from app.services.taxation_douaniere import calculer_liquidation

        return calculer_liquidation(
            valeur_en_douane=valeur_cif_xaf,
            db=db,
            code_sh=code_sh,
            regime=regime,
            origine=origine,
            categorie_tec=categorie_tec,
            taux_dd_explicite=taux_dd_explicite,
            # Quand la position SH est absente de la nomenclature (tables non
            # importees, cf. P1 #1), on retombe sur le taux "produit fini" 20%
            # MAIS le resultat est alors marque simulation=True / source_taux.
            defaut_dd_simulation=0.20,
        )
