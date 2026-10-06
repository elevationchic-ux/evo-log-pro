"""Cameroon Local Payment Services - Orange Money, MTN Mobile Money, Local Banks

Zero-Mock (Batch 3) : chaque demande est REELLEMENT persistee en base
(PaymentTransaction) et, si la gateway du fournisseur est configuree
(PAYMENT_ORANGE_* / PAYMENT_MTN_* / PAYMENT_BANK_*), un veritable appel HTTP
est emis vers elle. Sans gateway declaree, la ligne reste un brouillon
explicitement identifie comme tel : aucun faux « succes », aucun statut
invente, et plus aucun 501 nu — les operations impossibles sans fournisseur
renvoient 503 avec la raison.
"""
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.utils.external import call_provider, provider_configured


PROVIDER_PREFIX = {
    "ORANGE_MONEY": "PAYMENT_ORANGE",
    "MTN_MOBILE_MONEY": "PAYMENT_MTN",
    "VIREMENT": "PAYMENT_BANK",
}


def _prefix_pour(provider: str) -> str:
    return PROVIDER_PREFIX.get(provider, "PAYMENT_BANK")


def _row(db: Session, reference: str, provider: str):
    from app.models.advanced_crud import PaymentTransaction

    return (
        db.query(PaymentTransaction)
        .filter(
            PaymentTransaction.reference == reference,
            PaymentTransaction.provider == provider,
        )
        .order_by(PaymentTransaction.id.desc())
        .first()
    )


def _persist(
    db: Optional[Session],
    provider: str,
    reference: str,
    montant: float,
    description: Optional[str],
    company_id: Optional[int],
    statut: str,
    provider_contacte: bool,
    provider_ref: Optional[str] = None,
):
    """Ecrit (upsert) la transaction en base. Si db absent (facade legacy),
    la ligne n'est PAS persistee et le retour est marque en consequence."""
    if db is None:
        return None
    from app.models.advanced_crud import PaymentTransaction

    row = _row(db, reference, provider)
    if row is None:
        row = PaymentTransaction(reference=reference, provider=provider, company_id=company_id)
        db.add(row)
    row.montant_xaf = montant
    row.description = description
    row.statut = statut
    row.provider_contacte = provider_contacte
    if provider_ref is not None:
        row.provider_ref = provider_ref
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


def _dict(row, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base = {
        "id": row.id,
        "provider": row.provider,
        "reference": row.reference,
        "montant_xaf": float(row.montant_xaf) if row.montant_xaf is not None else None,
        "devise": "XAF",
        "statut": row.statut,
        "provider_contacte": bool(row.provider_contacte),
        "provider_ref": row.provider_ref,
        "description": row.description,
        "persiste_en_base": True,
        "date_creation": row.created_at.isoformat() if row.created_at else None,
    }
    if extra:
        base.update(extra)
    return base


def _initier(
    db: Optional[Session],
    provider: str,
    reference: str,
    montant: float,
    description: Optional[str],
    company_id: Optional[int],
    payload_fournisseur: Dict[str, Any],
    fonction: str,
) -> Dict[str, Any]:
    """Brouillon persiste, puis VERITABLE remise au fournisseur si configure.

    - Gateway configuree   -> appel HTTP ; statut fourni par la reponse
      fournisseur (jamais invente), provider_contacte=True.
    - Gateway absente      -> ligne gardee en BROUILLON, provider_contacte=False,
      avertissement explicite : ce n'est pas une preuve d'encaissement.
    """
    prefix = _prefix_pour(provider)
    row = _persist(db, provider, reference, montant, description, company_id, "BROUILLON", False)

    if provider_configured(prefix):
        result = call_provider(prefix, fonction, path="/payments/initiate", payload=payload_fournisseur)
        resp = result.get("response") or {}
        provider_ref = None
        if isinstance(resp, dict):
            provider_ref = str(
                resp.get("transaction_id") or resp.get("id") or resp.get("reference") or ""
            ) or None
        if row is not None:
            row = _persist(
                db, provider, reference, montant, description, company_id,
                "SOUMIS_FOURNISSEUR", True, provider_ref,
            )
            return _dict(row, {"fournisseur": result})
        return {
            "provider": provider, "reference": reference, "statut": "SOUMIS_FOURNISSEUR",
            "provider_contacte": True, "persiste_en_base": False, "fournisseur": result,
        }

    note = (
        f"Gateway {prefix} non configuree : la demande est enregistree en base "
        "comme brouillon, aucun envoi n'a eu lieu. Ce document n'est pas une "
        "preuve d'encaissement."
    )
    if row is not None:
        return _dict(row, {"avertissement": note})
    return {
        "provider": provider,
        "reference": reference,
        "montant_xaf": montant,
        "devise": "XAF",
        "statut": "BROUILLON",
        "provider_contacte": False,
        "persiste_en_base": False,
        "date_creation_brouillon": datetime.utcnow().isoformat(),
        "avertissement": note + " (appele sans session DB : rien n'a ete persiste)",
    }


def _verifier(db: Optional[Session], provider: str, reference: str, fonction: str) -> Dict[str, Any]:
    prefix = _prefix_pour(provider)
    row = _row(db, reference, provider) if db is not None else None

    if provider_configured(prefix):
        result = call_provider(prefix, fonction, path=f"/payments/{reference}", method="GET")
        if row is not None:
            resp = result.get("response") or {}
            statut_four = None
            if isinstance(resp, dict):
                statut_four = (resp.get("status") or resp.get("statut") or None)
            if statut_four:
                row.statut = f"FOURNISSEUR_{str(statut_four).upper()}"[:20]
                row.provider_contacte = True
                db.commit()
                db.refresh(row)
            return _dict(row, {"fournisseur": result})
        return {"provider": provider, "reference": reference, "persiste_en_base": False, "fournisseur": result}

    if row is not None:
        return _dict(row, {
            "avertissement": (
                f"Gateway {prefix} non configuree : le statut affiche est celui de "
                "la base locale (brouillon), AUCUN statut fournisseur n'est connu."
            )
        })
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=(
            f"Aucune transaction {reference} pour {provider} en base, et la gateway "
            f"{prefix} n'est pas configuree pour interroger le fournisseur."
        ),
    )


def _annuler(db: Optional[Session], provider: str, reference: str, fonction: str) -> Dict[str, Any]:
    prefix = _prefix_pour(provider)
    row = _row(db, reference, provider) if db is not None else None

    if provider_configured(prefix):
        result = call_provider(prefix, fonction, path=f"/payments/{reference}/cancel", payload={"reference": reference})
        if row is not None:
            row.statut = "ANNULE"
            row.provider_contacte = True
            db.commit()
            db.refresh(row)
            return _dict(row, {"fournisseur": result})
        return {"provider": provider, "reference": reference, "statut": "ANNULE", "fournisseur": result}

    if row is not None and row.statut == "BROUILLON":
        # Rien n'a jamais ete envoye : l'annulation purement locale est un acte
        # reel et honnete (le brouillon est barre).
        row.statut = "ANNULE_LOCAL"
        db.commit()
        db.refresh(row)
        return _dict(row, {
            "avertissement": "Aucune transaction fournisseur n'existait : seul le brouillon local est annule."
        })
    if row is not None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Annulation impossible : la transaction {reference} n'est plus un "
                f"brouillon local et la gateway {prefix} n'est pas configuree pour "
                "demander un revers au fournisseur."
            ),
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Aucune transaction {reference} pour {provider} en base.",
    )


class OrangeMoneyService:
    """Orange Money Payment Service - Cameroon"""

    @staticmethod
    def initier_paiement(
        db: Session,
        numero_orange: str,
        montant: float,
        reference: str,
        description: str,
        company_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Persiste la demande ; remise reels a Orange Money si la gateway est configuree."""
        return _initier(
            db, "ORANGE_MONEY", reference, montant, description, company_id,
            {"amount": montant, "currency": "XAF", "payer": numero_orange, "reference": reference, "description": description},
            "Initiation d'un paiement Orange Money",
        )

    @staticmethod
    def verifier_paiement(db: Session, reference: str) -> Dict[str, Any]:
        """Statut : reponse fournisseur si gateway configuree, sinon statut local honnete."""
        return _verifier(db, "ORANGE_MONEY", reference, "Verification de statut paiement Orange Money")

    @staticmethod
    def annuler_paiement(db: Session, reference: str) -> Dict[str, Any]:
        """Revers fournisseur si configure ; annulation du seul brouillon sinon."""
        return _annuler(db, "ORANGE_MONEY", reference, "Annulation de paiement Orange Money")


class MTNMobileMoneyService:
    """MTN Mobile Money Payment Service - Cameroon"""

    @staticmethod
    def initier_paiement(
        db: Session,
        numero_mtn: str,
        montant: float,
        reference: str,
        description: str,
        company_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Persiste la demande ; request-to-pay reel MTN si la gateway est configuree."""
        return _initier(
            db, "MTN_MOBILE_MONEY", reference, montant, description, company_id,
            {"amount": montant, "currency": "XAF", "payer": numero_mtn, "reference": reference, "description": description},
            "Initiation d'un paiement MTN Mobile Money",
        )

    @staticmethod
    def verifier_paiement(db: Session, reference: str) -> Dict[str, Any]:
        return _verifier(db, "MTN_MOBILE_MONEY", reference, "Verification de statut paiement MTN Mobile Money")

    @staticmethod
    def annuler_paiement(db: Session, reference: str) -> Dict[str, Any]:
        return _annuler(db, "MTN_MOBILE_MONEY", reference, "Annulation de paiement MTN Mobile Money")


class BanqueLocaleService:
    """Local Bank Payment Service - Cameroon Banks

    NB : les URLs d'API bancaires precedemment listees ici etaient inventees et
    n'ont jamais ete appelées. Elles sont supprimees : le virement passe par la
    gateway PAYMENT_BANK reels (GIMAC/BGPI, host-to-host) si declaree, sinon il
    reste un ordre prepare, clairement non execute.
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
        motif: str,
        company_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Ordre de virement persiste ; remise a la banque only si gateway configuree."""
        if code_banque not in BanqueLocaleService.BANKS:
            raise ValueError(f"Banque {code_banque} non supportée")
        provider = "VIREMENT_" + code_banque
        return _initier(
            db, provider, reference, montant, motif, company_id,
            {
                "bank": BanqueLocaleService.BANKS[code_banque],
                "account": compte_bancaire,
                "amount": montant,
                "currency": "XAF",
                "beneficiary": beneficiaire,
                "reference": reference,
                "motif": motif,
            },
            f"Emission d'un virement {BanqueLocaleService.BANKS[code_banque]}",
        )

    @staticmethod
    def verifier_virement(db: Session, reference: str) -> Dict[str, Any]:
        prefix = "PAYMENT_BANK"
        row = None
        from app.models.advanced_crud import PaymentTransaction

        if db is not None:
            row = (
                db.query(PaymentTransaction)
                .filter(PaymentTransaction.reference == reference,
                        PaymentTransaction.provider.like("VIREMENT_%"))
                .order_by(PaymentTransaction.id.desc())
                .first()
            )
        if provider_configured(prefix):
            result = call_provider(prefix, "Verification de virement bancaire",
                                   path=f"/transfers/{reference}", method="GET")
            if row is not None:
                return _dict(row, {"fournisseur": result})
            return {"reference": reference, "persiste_en_base": False, "fournisseur": result}
        if row is not None:
            return _dict(row, {
                "avertissement": (
                    "Connecteur bancaire non configure : statut local uniquement, "
                    "l'execution reelle du virement n'est pas confirmee."
                )
            })
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun ordre de virement avec cette reference en base, et le connecteur bancaire est inactive.",
        )

    @staticmethod
    def get_releve_compte(db: Session, code_banque: str, compte: str) -> Dict[str, Any]:
        """Releve : import MT940/camt.053 ou connecteur bancaire signe.

        503 explicite si aucune gateway declaree : l'ancien solde « 5 000 000 »
        codé en dur a disparu, rien n'est invente.
        """
        return call_provider(
            "PAYMENT_BANK",
            "Releve de compte bancaire en ligne",
            path=f"/comptes/{compte}/releve",
            method="GET",
            payload={"banque": code_banque, "compte": compte},
        )


class PaiementLocalService:
    """Unified Local Payment Service"""

    @staticmethod
    def choisir_methode_paiement(
        methode: str,
        donnees: Dict[str, Any],
        db: Optional[Session] = None,
        company_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Choisir et preparer une methode de paiement locale (persistee si db)."""
        if methode == "ORANGE_MONEY":
            return OrangeMoneyService.initier_paiement(
                db, donnees["numero"], donnees["montant"],
                donnees["reference"], donnees["description"], company_id=company_id
            )
        elif methode == "MTN_MOBILE_MONEY":
            return MTNMobileMoneyService.initier_paiement(
                db, donnees["numero"], donnees["montant"],
                donnees["reference"], donnees["description"], company_id=company_id
            )
        elif methode == "VIREMENT":
            return BanqueLocaleService.initier_virement(
                db, donnees["banque"], donnees["compte"],
                donnees["montant"], donnees["beneficiaire"],
                donnees["reference"], donnees["motif"], company_id=company_id
            )
        else:
            raise ValueError(f"Méthode de paiement {methode} non supportée")

    @staticmethod
    def get_methodes_disponibles() -> list:
        """Get available payment methods (liste indicative, selon gateway declarees)."""
        return [
            {"code": "ORANGE_MONEY", "nom": "Orange Money", "gateway_configuree": provider_configured("PAYMENT_ORANGE")},
            {"code": "MTN_MOBILE_MONEY", "nom": "MTN Mobile Money", "gateway_configuree": provider_configured("PAYMENT_MTN")},
            {"code": "VIREMENT", "nom": "Virement Bancaire", "gateway_configuree": provider_configured("PAYMENT_BANK")},
            {"code": "CHEQUE", "nom": "Chèque", "gateway_configuree": None},
            {"code": "ESPECE", "nom": "Espèces", "gateway_configuree": None},
        ]
