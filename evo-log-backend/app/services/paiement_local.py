"""Cameroon Local Payment Services - Orange Money, MTN Mobile Money, Local Banks

AUCUN FAUX SUCCÈS (2026-09 correction) :
Ce module ne communique avec aucun fournisseur (aucune API MoMo/Orange/banque
n'est appelée, aucun paiement n'est persisté). Il prépare uniquement des
« brouillons d'encaissement » clairement identifiés comme tels. Les
vérifications de statut, annulations, exécutions de virement et relevés
bancaires renvoient 501 tant qu'un connecteur réel n'est pas déployé 
l'ancien code renvoyait « succes » inconditionnellement, ce qui laissait
croire encaissées des sommes ne l'étant pas.
"""
from datetime import datetime, date
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.not_implemented import not_implemented


def _brouillon_paiement(provider: str, **kwargs) -> Dict[str, Any]:
    """Construit un brouillon d'encaissement  jamais un paiement confirmé."""
    return {
        **kwargs,
        "provider": provider,
        "devise": "XAF",
        "statut": "BROUILLON_LOCAL",
        "provider_contacte": False,
        "persiste_en_base": False,
        "date_creation_brouillon": datetime.utcnow(),
        "avertissement": (
            "Aucun échange n'a eu lieu avec le fournisseur de paiement. "
            "Ce document n'est pas une preuve d'encaissement."
        ),
    }


class OrangeMoneyService:
    """Orange Money Payment Service - Cameroon"""
    
    @staticmethod
    def initier_paiement(
        db: Session,
        numero_orange: str,
        montant: float,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Prépare un brouillon de paiement Orange Money (aucune API appelée)."""
        return _brouillon_paiement(
            "ORANGE_MONEY",
            numero=numero_orange,
            montant=montant,
            reference=reference,
            description=description,
        )
    
    @staticmethod
    def verifier_paiement(reference: str) -> Dict[str, Any]:
        """Vérifier statut paiement Orange Money."""
        not_implemented(
            "Vérification de statut de paiement Orange Money",
            "connecteur API Orange Money Cameroun (consentement, callback signé, "
            "persistances des transactions)  aucun statut n'est connu sans lui",
        )
    
    @staticmethod
    def annuler_paiement(reference: str) -> Dict[str, Any]:
        """Annuler paiement Orange Money."""
        not_implemented(
            "Annulation de paiement Orange Money",
            "API reversée du fournisseur et registre persistant des transactions",
        )


class MTNMobileMoneyService:
    """MTN Mobile Money Payment Service - Cameroon"""
    
    @staticmethod
    def initier_paiement(
        db: Session,
        numero_mtn: str,
        montant: float,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Prépare un brouillon de paiement MTN Mobile Money (aucune API appelée)."""
        return _brouillon_paiement(
            "MTN_MOBILE_MONEY",
            numero=numero_mtn,
            montant=montant,
            reference=reference,
            description=description,
        )
    
    @staticmethod
    def verifier_paiement(reference: str) -> Dict[str, Any]:
        """Vérifier statut paiement MTN Mobile Money."""
        not_implemented(
            "Vérification de statut de paiement MTN Mobile Money",
            "connecteur API MTN MoMo Cameroun (request-to-pay, callback signé, "
            "journal des transactions persisté)",
        )
    
    @staticmethod
    def annuler_paiement(reference: str) -> Dict[str, Any]:
        """Annuler paiement MTN Mobile Money."""
        not_implemented(
            "Annulation de paiement MTN Mobile Money",
            "API reversée du fournisseur et registre persistant des transactions",
        )


class BanqueLocaleService:
    """Local Bank Payment Service - Cameroon Banks

    NB : les URLs d'API bancaires précédemment listées ici étaient inventées
    et n'ont jamais été appelées. Elles sont supprimées : aucun connecteur
    bancaire (GIMAC/BGPI, host2host) n'est déployé.
    """
    
    BANKS = {
        "SG": "Société Générale Cameroun",
        "BICEC": "BICEC",
        "AFRILAND": "Afriland First Bank",
        "SCB": "SCB Cameroun",
        "ECOBANK": "Ecobank Cameroun",
        "BGFI": "BGFI Bank"
    }
    
    @staticmethod
    def initier_virement(
        db: Session,
        code_banque: str,
        compte_bancaire: str,
        montant: float,
        beneficiaire: str,
        reference: str,
        motif: str
    ) -> Dict[str, Any]:
        """Prépare un brouillon d'ordre de virement (aucune banque contactée)."""
        if code_banque not in BanqueLocaleService.BANKS:
            raise ValueError(f"Banque {code_banque} non supportée")
        
        return _brouillon_paiement(
            "VIREMENT_" + code_banque,
            banque=BanqueLocaleService.BANKS[code_banque],
            compte=compte_bancaire,
            montant=montant,
            beneficiaire=beneficiaire,
            reference=reference,
            motif=motif,
        )
    
    @staticmethod
    def verifier_virement(reference: str) -> Dict[str, Any]:
        """Vérifier statut virement."""
        not_implemented(
            "Vérification de virement bancaire",
            "connecteur bancaire (GIMAC/BGPI ou host-to-host par banque) et "
            "journal des ordres persisté en base",
        )
    
    @staticmethod
    def get_releve_compte(code_banque: str, compte: str) -> Dict[str, Any]:
        """Obtenir relevé de compte."""
        not_implemented(
            "Relevé de compte bancaire en ligne",
            "import de relevés (MT940/camt.053) ou connecteur bancaire signé  "
            "l'ancien solde « 5 000 000 » était une valeur codée en dur",
        )


class PaiementLocalService:
    """Unified Local Payment Service"""
    
    @staticmethod
    def choisir_methode_paiement(
        methode: str,
        donnees: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Choisir et exécuter méthode de paiement locale"""
        if methode == "ORANGE_MONEY":
            return OrangeMoneyService.initier_paiement(
                None, donnees["numero"], donnees["montant"],
                donnees["reference"], donnees["description"]
            )
        elif methode == "MTN_MOBILE_MONEY":
            return MTNMobileMoneyService.initier_paiement(
                None, donnees["numero"], donnees["montant"],
                donnees["reference"], donnees["description"]
            )
        elif methode == "VIREMENT":
            return BanqueLocaleService.initier_virement(
                None, donnees["banque"], donnees["compte"],
                donnees["montant"], donnees["beneficiaire"],
                donnees["reference"], donnees["motif"]
            )
        else:
            raise ValueError(f"Méthode de paiement {methode} non supportée")
    
    @staticmethod
    def get_methodes_disponibles() -> list:
        """Get available payment methods"""
        return [
            {"code": "ORANGE_MONEY", "nom": "Orange Money", "icon": "🍊"},
            {"code": "MTN_MOBILE_MONEY", "nom": "MTN Mobile Money", "icon": "📱"},
            {"code": "VIREMENT", "nom": "Virement Bancaire", "icon": "🏦"},
            {"code": "CHEQUE", "nom": "Chèque", "icon": "📄"},
            {"code": "ESPECE", "nom": "Espèces", "icon": "💵"}
        ]
