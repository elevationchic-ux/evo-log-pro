"""Numerotation legale des pieces (factures, avoirs, reglements).

Usage :
    numero = prochaine_reference(db, "FACTURE", company_id=user.company_id,
                                 date_reference=facture.date_emission)
    # -> "FAC-2026-0001", "FAC-2026-0002", ... sans trou possible

Garanties (exigence DGI / OHADA) :
    • sequence **continue** par entreprise, type de piece et annee civile ;
    • l'increment se fait dans la MEME transaction que la creation de la
      piece : un echec (rollback) ne consomme aucun numero, donc aucun trou ;
    • au premier appel, le compteur est **amorce au max existant** du meme
      prefixe/annee : impossible d'attribuer un numero deja pose sur une
      facture historique.

Ne pas " ameliorer " avec un uuid/timestamp : ce serait exactement la
derive que cette correction supprime.
"""
from datetime import date
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.numerotation import SequenceNumerotation

# Type de piece -> prefixe legal d'usage (CGI Cameroun, pratique DGI).
PREFIXES_PAR_TYPE = {
    "FACTURE": "FAC",
    "AVOIR": "AV",
    "REGLEMENT": "REC",
}


def _numero_max_deja_pose(
    db: Session, prefixe: str, annee: int, company_id: Optional[int]
) -> int:
    """Plus grand suffixe numerique deja utilise pour "<prefixe>-<annee>-XXXX".

    Balaie les deux tables de factures du systeme (ohada + legacy) afin
    qu'aucun numero historique ne puisse etre re-attribue.
    """
    patron = f"{prefixe}-{annee}-"
    maximum = 0

    from app.models.finance_ohada import FactureNew
    from app.models.finance import Facture as FactureLegale

    for model in (FactureNew, FactureLegale):
        query = db.query(model.numero_facture).filter(model.numero_facture.like(patron + "%"))
        if model is FactureLegale and company_id is not None:
            # La table legacy porte le rattachement entreprise ; pas la table OHADA.
            query = query.filter(model.company_id == company_id)
        for (numero,) in query.all():
            suffixe = str(numero)[len(patron):]
            if suffixe.isdigit():
                maximum = max(maximum, int(suffixe))
    return maximum


def prochaine_reference(
    db: Session,
    type_document: str,
    company_id: Optional[int] = None,
    date_reference: Optional[date] = None,
    prefixe: Optional[str] = None,
) -> str:
    """Retourne le prochain numero legal et reserve le compteur.

    N'appelle PAS commit : la reservation vit dans la transaction du
    caller (creation de la piece). Rollback = numero restitue.
    """
    type_document = (type_document or "").upper()
    prefixe = prefixe or PREFIXES_PAR_TYPE.get(type_document)
    if not prefixe:
        raise HTTPException(
            status_code=400,
            detail=f"Type de piece non numerote par le systeme : '{type_document}'.",
        )

    annee = (date_reference or date.today()).year

    seq = (
        db.query(SequenceNumerotation)
        .filter(
            SequenceNumerotation.company_id.is_(None)
            if company_id is None
            else SequenceNumerotation.company_id == company_id,
            SequenceNumerotation.type_document == type_document,
            SequenceNumerotation.exercice == annee,
        )
        .with_for_update()  # ignore silencieusement sur SQLite, reel sur PostgreSQL
        .first()
    )

    if seq is None:
        seq = SequenceNumerotation(
            company_id=company_id,
            type_document=type_document,
            exercice=annee,
            prefixe=prefixe,
            courant=_numero_max_deja_pose(db, prefixe, annee, company_id),
        )
        db.add(seq)
        db.flush()

    seq.courant += 1
    db.flush()
    return f"{prefixe}-{annee}-{seq.courant:04d}"
