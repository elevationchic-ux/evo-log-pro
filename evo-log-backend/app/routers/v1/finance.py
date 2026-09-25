"""Finance router - OHADA accounting and financial management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.finance import (
    PlanComptableOHADACreate, PlanComptableOHADAUpdate, PlanComptableOHADAResponse,
    EcritureComptableCreate, EcritureComptableUpdate, EcritureComptableResponse,
    ExerciceComptableCreate, ExerciceComptableUpdate, ExerciceComptableResponse,
    FactureCreate, FactureUpdate, FactureResponse,
    LigneFactureCreate, LigneFactureUpdate, LigneFactureResponse,
    ReglementCreate, ReglementUpdate, ReglementResponse,
    TVADeclarableCreate, TVADeclarableUpdate, TVADeclarableResponse,
    RetenueSourceCreate, RetenueSourceUpdate, RetenueSourceResponse,
    ISDeclarableCreate, ISDeclarableUpdate, ISDeclarableResponse,
    CentimesAdditionnelsCreate, CentimesAdditionnelsUpdate, CentimesAdditionnelsResponse,
    PatenteCreate, PatenteUpdate, PatenteResponse,
    BilanCreate, BilanUpdate, BilanResponse,
    CompteResultatCreate, CompteResultatUpdate, CompteResultatResponse,
    SignatureElectroniqueCreate, SignatureElectroniqueUpdate, SignatureElectroniqueResponse,
    RapportFiscalResponse
)
from app.services.finance_service import (
    PlanComptableOHADAService, EcritureComptableService, ExerciceComptableService, FactureService,
    ReglementService, TVADeclarableService, RetenueSourceService, ISDeclarableService,
    CentimesAdditionnelsService, PatenteService, BilanService, CompteResultatService,
    SignatureElectroniqueService, FinanceReportingService
)
from app.models.finance_ohada import PlanComptableOHADA, EcritureComptableNew as EcritureComptable, ExerciceComptable, FactureNew as Facture, RetenueSource

# Pas de prefix ici : main.py monte deja ce routeur sur /api/v1/finance
# (et /api/finance pour l'alias deprecie). Un prefix double creait des routes
# /api/v1/finance/finance/... injoignables depuis le frontend.
router = APIRouter(tags=["Finance"])


# ============ PLAN COMPTABLE OHADA ============
@router.post("/plan-comptable", response_model=PlanComptableOHADAResponse, status_code=status.HTTP_201_CREATED)
def creer_compte(
    compte: PlanComptableOHADACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create OHADA account"""
    return PlanComptableOHADAService.creer_compte(
        db, compte.numero_compte, compte.intitule, compte.type_compte,
        compte.classe, compte.sous_classe
    )


@router.put("/plan-comptable/{compte_id}", response_model=PlanComptableOHADAResponse)
def mettre_a_jour_compte(
    compte_id: int,
    compte: PlanComptableOHADAUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update OHADA account"""
    c = db.query(PlanComptableOHADA).filter(PlanComptableOHADA.id == compte_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Compte non trouvé")
    
    for field, value in compte.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ ECRITURES COMPTABLES ============
@router.post("/ecritures", response_model=EcritureComptableResponse, status_code=status.HTTP_201_CREATED)
def creer_ecriture(
    ecriture: EcritureComptableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create accounting entry"""
    return EcritureComptableService.creer_ecriture(
        db, ecriture.numero_ecriture, ecriture.date_ecriture, ecriture.libelle,
        ecriture.compte_id, ecriture.debit, ecriture.credit, ecriture.journal, ecriture.periode
    )


@router.put("/ecritures/{ecriture_id}/valider", response_model=EcritureComptableResponse)
def valider_ecriture(
    ecriture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate accounting entry"""
    return EcritureComptableService.valider_ecriture(db, ecriture_id, current_user.username)


@router.put("/ecritures/{ecriture_id}", response_model=EcritureComptableResponse)
def mettre_a_jour_ecriture(
    ecriture_id: int,
    ecriture: EcritureComptableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update accounting entry"""
    e = db.query(EcritureComptable).filter(EcritureComptable.id == ecriture_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Écriture non trouvée")
    
    for field, value in ecriture.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


# ============ EXERCICES COMPTABLES ============
@router.post("/exercices", response_model=ExerciceComptableResponse, status_code=status.HTTP_201_CREATED)
def creer_exercice(
    exercice: ExerciceComptableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create fiscal year"""
    return ExerciceComptableService.creer_exercice(
        db, exercice.numero_exercice, exercice.annee,
        exercice.date_debut, exercice.date_fin
    )


@router.put("/exercices/{exercice_id}/cloturer", response_model=ExerciceComptableResponse)
def cloturer_exercice(
    exercice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close fiscal year"""
    return ExerciceComptableService.cloturer_exercice(db, exercice_id, current_user.username)


@router.put("/exercices/{exercice_id}", response_model=ExerciceComptableResponse)
def mettre_a_jour_exercice(
    exercice_id: int,
    exercice: ExerciceComptableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update fiscal year"""
    e = db.query(ExerciceComptable).filter(ExerciceComptable.id == exercice_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")
    
    for field, value in exercice.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


# ============ FACTURES ============
@router.post("/factures", response_model=FactureResponse, status_code=status.HTTP_201_CREATED)
def creer_facture(
    facture: FactureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une facture.

    Numéro absent -> séquence légale continue FAC-ANNEE-000X (exigence DGI) ;
    le numéro saisi manuellement n'est accepté que s'il est unique (contrainte
    base).
    """
    return FactureService.creer_facture(
        db, facture.numero_facture, facture.client_id, facture.type_facture,
        facture.date_emission, facture.montant_ht, facture.taux_tva
    )


@router.post("/factures/{facture_id}/lignes", response_model=LigneFactureResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne_facture(
    facture_id: int,
    ligne: LigneFactureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add line to invoice"""
    return FactureService.ajouter_ligne_facture(
        db, facture_id, ligne.article_id, ligne.designation,
        ligne.quantite, ligne.prix_unitaire_ht, ligne.taux_tva
    )


@router.put("/factures/{facture_id}", response_model=FactureResponse)
def mettre_a_jour_facture(
    facture_id: int,
    facture: FactureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update invoice"""
    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    
    for field, value in facture.model_dump(exclude_unset=True).items():
        setattr(f, field, value)
    
    db.commit()
    db.refresh(f)
    return f


@router.get("/factures/{facture_id}/pdf")
def telecharger_facture_pdf(
    facture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Télécharger la facture au format PDF (mentions DGI/OHADA incluses).

    Retourne un HTTP 501 honnête si la chaîne de génération PDF (WeasyPrint +
    Pango/Cairo) n'est pas disponible dans l'environnement courant  jamais un
    faux PDF ni du HTML déguisé.
    """
    from fastapi import Response
    from app.models.tiers import Tiers
    from app.models.tenant import Company
    from app.utils.pdf_generator import generer_pdf, montant_en_lettres

    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    client = db.query(Tiers).filter(Tiers.id == f.client_id).first() if f.client_id else None
    company = db.query(Company).filter(Company.id == current_user.company_id).first() \
        if getattr(current_user, "company_id", None) else None

    pdf = generer_pdf("facture.html.j2", {
        "facture": f,
        "client": client,
        "company": company,
        "lignes": f.lignes_facture or [],
        "taux_tva": float(f.taux_tva or 0),
        "montant_en_lettres": montant_en_lettres(f.montant_ttc, f.devise or "XAF"),
    })
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="facture-{f.numero_facture}.pdf"'},
    )


# ============ REGLEMENTS ============
@router.post("/reglements", response_model=ReglementResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_reglement(
    reglement: ReglementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record payment"""
    return ReglementService.enregistrer_reglement(
        db, reglement.numero_reglement, reglement.facture_id,
        reglement.date_reglement, reglement.montant, reglement.mode_paiement, current_user.username
    )


@router.put("/reglements/{reglement_id}", response_model=ReglementResponse)
def mettre_a_jour_reglement(
    reglement_id: int,
    reglement: ReglementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update payment"""
    r = db.query(Reglement).filter(Reglement.id == reglement_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Règlement non trouvé")
    
    for field, value in reglement.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    
    db.commit()
    db.refresh(r)
    return r


# ============ TVA DECLARABLE ============
@router.post("/tva-declarations", response_model=TVADeclarableResponse, status_code=status.HTTP_201_CREATED)
def creer_declaration_tva(
    declaration: TVADeclarableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create VAT declaration"""
    return TVADeclarableService.creer_declaration_tva(
        db, declaration.numero_declaration, declaration.periode, declaration.regime_tva,
        declaration.base_imposable, declaration.tva_collectee, declaration.tva_deductible
    )


@router.put("/tva-declarations/{declaration_id}", response_model=TVADeclarableResponse)
def mettre_a_jour_declaration_tva(
    declaration_id: int,
    declaration: TVADeclarableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update VAT declaration"""
    d = db.query(TVADeclarable).filter(TVADeclarable.id == declaration_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Déclaration TVA non trouvée")
    
    for field, value in declaration.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ RETENUES SOURCE ============
@router.post("/retenues-source", response_model=RetenueSourceResponse, status_code=status.HTTP_201_CREATED)
def creer_retenue_source(
    retenue: RetenueSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create withholding tax"""
    return RetenueSourceService.creer_retenue_source(
        db, retenue.numero_retenu, retenue.facture_id, retenue.date_retenu,
        retenue.type_retenu, retenue.taux_retenu, retenue.base_imposable
    )


@router.put("/retenues-source/{retenue_id}", response_model=RetenueSourceResponse)
def mettre_a_jour_retenue_source(
    retenue_id: int,
    retenue: RetenueSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update withholding tax"""
    r = db.query(RetenueSource).filter(RetenueSource.id == retenue_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Retenue source non trouvée")
    
    for field, value in retenue.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    
    db.commit()
    db.refresh(r)
    return r


# ============ IS DECLARABLE ============
@router.post("/is-declarations", response_model=ISDeclarableResponse, status_code=status.HTTP_201_CREATED)
def creer_declaration_is(
    declaration: ISDeclarableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create corporate tax declaration"""
    return ISDeclarableService.creer_declaration_is(
        db, declaration.numero_declaration, declaration.exercice_id,
        declaration.annee, declaration.regime_is, declaration.benefice_fiscal
    )


@router.put("/is-declarations/{declaration_id}", response_model=ISDeclarableResponse)
def mettre_a_jour_declaration_is(
    declaration_id: int,
    declaration: ISDeclarableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update corporate tax declaration"""
    d = db.query(ISDeclarable).filter(ISDeclarable.id == declaration_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Déclaration IS non trouvée")
    
    for field, value in declaration.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ CENTIMES ADDITIONNELS ============
@router.post("/centimes-additionnels", response_model=CentimesAdditionnelsResponse, status_code=status.HTTP_201_CREATED)
def creer_centimes(
    centimes: CentimesAdditionnelsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create additional local tax"""
    return CentimesAdditionnelsService.creer_centimes(
        db, centimes.numero_taxe, centimes.periode, centimes.type_taxe,
        centimes.base_imposable, centimes.taux, centimes.collectivite
    )


@router.put("/centimes-additionnels/{centimes_id}", response_model=CentimesAdditionnelsResponse)
def mettre_a_jour_centimes(
    centimes_id: int,
    centimes: CentimesAdditionnelsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update additional local tax"""
    c = db.query(CentimesAdditionnels).filter(CentimesAdditionnels.id == centimes_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Centimes additionnels non trouvés")
    
    for field, value in centimes.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ PATENTE ============
@router.post("/patentes", response_model=PatenteResponse, status_code=status.HTTP_201_CREATED)
def creer_patente(
    patente: PatenteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create business license tax"""
    return PatenteService.creer_patente(
        db, patente.numero_patente, patente.entreprise_id, patente.annee,
        patente.categorie, patente.chiffre_affaires, patente.montant_patente
    )


@router.put("/patentes/{patente_id}", response_model=PatenteResponse)
def mettre_a_jour_patente(
    patente_id: int,
    patente: PatenteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update business license tax"""
    p = db.query(Patente).filter(Patente.id == patente_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patente non trouvée")
    
    for field, value in patente.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ BILAN ============
@router.post("/bilans", response_model=BilanResponse, status_code=status.HTTP_201_CREATED)
def creer_bilan(
    bilan: BilanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create balance sheet"""
    return BilanService.creer_bilan(
        db, bilan.exercice_id, bilan.date_bilan, bilan.total_actif, bilan.total_passif
    )


@router.put("/bilans/{bilan_id}", response_model=BilanResponse)
def mettre_a_jour_bilan(
    bilan_id: int,
    bilan: BilanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update balance sheet"""
    b = db.query(Bilan).filter(Bilan.id == bilan_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bilan non trouvé")
    
    for field, value in bilan.model_dump(exclude_unset=True).items():
        setattr(b, field, value)
    
    db.commit()
    db.refresh(b)
    return b


# ============ COMPTE RESULTAT ============
@router.post("/comptes-resultat", response_model=CompteResultatResponse, status_code=status.HTTP_201_CREATED)
def creer_compte_resultat(
    compte: CompteResultatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create income statement"""
    return CompteResultatService.creer_compte_resultat(
        db, compte.exercice_id, compte.periode, compte.chiffre_affaires,
        compte.achats, compte.resultat_net
    )


@router.put("/comptes-resultat/{compte_id}", response_model=CompteResultatResponse)
def mettre_a_jour_compte_resultat(
    compte_id: int,
    compte: CompteResultatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update income statement"""
    c = db.query(CompteResultat).filter(CompteResultat.id == compte_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Compte de résultat non trouvé")
    
    for field, value in compte.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ SIGNATURE ELECTRONIQUE ============
@router.post("/signatures-electroniques", response_model=SignatureElectroniqueResponse, status_code=status.HTTP_201_CREATED)
def signer_facture(
    signature: SignatureElectroniqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sign invoice electronically"""
    return SignatureElectroniqueService.signer_facture(
        db, signature.facture_id, signature.numero_signature,
        signature.emetteur, signature.certificat_id
    )


@router.put("/signatures-electroniques/{signature_id}", response_model=SignatureElectroniqueResponse)
def mettre_a_jour_signature(
    signature_id: int,
    signature: SignatureElectroniqueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update electronic signature"""
    s = db.query(SignatureElectronique).filter(SignatureElectronique.id == signature_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Signature non trouvée")
    
    for field, value in signature.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    
    db.commit()
    db.refresh(s)
    return s


@router.get("/exercices/{exercice_id}/rapport-fiscal", response_model=RapportFiscalResponse)
def rapport_fiscal(
    exercice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate fiscal report"""
    return FinanceReportingService.rapport_fiscal(db, exercice_id)


# ============ KPIS & ANALYTICS ============
@router.get("/factures")
def list_factures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des factures d'exploitation du tenant courant (lecture reelle en base)."""
    from app.models.finance import Facture as FactureSimple

    factures = (
        db.query(FactureSimple)
        .order_by(FactureSimple.date_emission.desc(), FactureSimple.id.desc())
        .limit(500)
        .all()
    )
    return [
        {
            "id": f.id,
            "numero_facture": f.numero_facture,
            "client_id": f.client_id,
            "client_nom": (f.client.name if f.client else None),
            "date_emission": f.date_emission.isoformat() if f.date_emission else None,
            "date_echeance": f.date_echeance.isoformat() if f.date_echeance else None,
            "montant_ht": float(f.montant_ht or 0),
            "montant_tva": float(f.montant_tva or 0),
            "montant_ttc": float(f.montant_ttc or 0),
            "statut": (f.statut.value if hasattr(f.statut, "value") else str(f.statut)),
        }
        for f in factures
    ]


@router.get("/encaissements")
def list_encaissements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des reglements/encaissements du tenant courant (table paiements)."""
    from app.models.finance import Paiement

    paiements = (
        db.query(Paiement)
        .order_by(Paiement.date_paiement.desc(), Paiement.id.desc())
        .limit(500)
        .all()
    )
    return [
        {
            "id": p.id,
            "facture_id": p.facture_id,
            "montant": float(p.montant or 0),
            "date_paiement": p.date_paiement.isoformat() if p.date_paiement else None,
            "mode_paiement": p.mode_paiement,
            "reference": p.reference,
            "statut": (p.statut.value if hasattr(p.statut, "value") else str(p.statut)),
        }
        for p in paiements
    ]


@router.get("/kpis")
def get_finance_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """KPIs financiers consolidés pour les tableaux de bord.

    100% agrégé depuis la base (filtrée par le tenant courant via le filtre
    ORM global). Aucune valeur par défaut inventée : sans écritures, les KPI
    retournent 0, ce qui reflète l'état réel du dossier.
    """
    from sqlalchemy import func
    from datetime import timedelta
    from app.models.finance import Facture as FactureSimple, Paiement, Compte, FactureStatus
    from app.models.finance_ohada import FactureNew

    # Chiffre d'affaires : cumuls réels des deux modèles de factures.
    ca_ohada = float(db.query(func.sum(FactureNew.montant_ttc)).scalar() or 0.0)
    ca_simple = float(db.query(func.sum(FactureSimple.montant_ttc)).scalar() or 0.0)
    chiffre_affaires = ca_ohada + ca_simple

    total_factures = (
        (db.query(func.count(FactureNew.id)).scalar() or 0)
        + (db.query(func.count(FactureSimple.id)).scalar() or 0)
    )
    total_encaisse = float(db.query(func.sum(Paiement.montant)).scalar() or 0.0)

    impayes = max(0.0, chiffre_affaires - total_encaisse)
    taux_recouvrement = round((total_encaisse / chiffre_affaires * 100), 1) if chiffre_affaires > 0 else 0.0

    # Trésorerie disponible : solde cumulé des comptes de classe 5 (banque/caisse).
    tresorerie_disponible = float(
        db.query(func.sum(Compte.solde)).filter(Compte.numero_compte.like("5%")).scalar() or 0.0
    )

    # Créances douteuses : factures simples impayées échues depuis plus de 90 jours.
    seuil = date.today() - timedelta(days=90)
    creances_douteuses = float(
        db.query(func.sum(FactureSimple.montant_ttc))
        .filter(
            FactureSimple.date_echeance < seuil,
            FactureSimple.statut.notin_([
                FactureStatus.PAYEE, FactureStatus.ANNULEE, FactureStatus.BROUILLON
            ]),
        )
        .scalar() or 0.0
    )

    return {
        "chiffre_affaires": chiffre_affaires,
        "total_factures": total_factures,
        "total_encaisse": total_encaisse,
        "montant_impaye": impayes,
        "taux_recouvrement": taux_recouvrement,
        "creances_douteuses": creances_douteuses,
        "tresorerie_disponible": tresorerie_disponible,
    }


@router.get("/analytics/chart-data")
def get_finance_chart_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Séries temporelles de chiffre d'affaires, agrégées par mois réel.

    Basé sur les factures d'exploitation (Facture) : le CA mensuel (en millions
    de XAF) est calculé depuis les pièces saisies, sans série codée en dur.
    """
    from app.models.finance import Facture as FactureSimple

    rows = db.query(FactureSimple.date_emission, FactureSimple.montant_ttc).all()

    monthly: dict[str, float] = {}
    for d, montant in rows:
        if not d:
            continue
        key = f"{d.year:04d}-{d.month:02d}"
        monthly[key] = monthly.get(key, 0.0) + float(montant or 0.0)

    # 12 derniers mois, dans l'ordre chronologique.
    today = date.today()
    series = []
    for offset in range(11, -1, -1):
        y = today.year
        m = today.month - offset
        while m <= 0:
            m += 12
            y -= 1
        key = f"{y:04d}-{m:02d}"
        series.append({
            "month": key,
            "revenue": round(monthly.get(key, 0.0) / 1_000_000.0, 2),
        })

    return {
        "source": "factures",
        "currency_unit": "M XAF",
        "months": series,
    }

