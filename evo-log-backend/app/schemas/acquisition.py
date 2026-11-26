"""Pydantic schemas for Acquisition module - Procurement and supplier management"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Appel Offres schemas
class AppelOffresBase(BaseModel):
    numero_appel: str
    titre: str
    type_appel: str
    budget_estime: float
    date_limite: date
    responsable: str
    departement: str
    description: str


class AppelOffresCreate(AppelOffresBase):
    documents_requis: str = ""
    conditions_participation: str = ""


class AppelOffresUpdate(BaseModel):
    statut: Optional[str] = None
    date_publication: Optional[date] = None
    date_ouverture: Optional[date] = None
    date_attribution: Optional[date] = None
    conditions_participation: Optional[str] = None
    documents_requis: Optional[str] = None


class AppelOffresResponse(AppelOffresBase):
    id: int
    devise: str
    date_publication: Optional[date] = None
    date_ouverture: Optional[date] = None
    date_attribution: Optional[date] = None
    documents_requis: Optional[str] = None
    conditions_participation: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Cahier Charges schemas
class CahierChargesBase(BaseModel):
    numero_cdc: str
    appel_offres_id: int
    objet: str
    description_technique: str
    specifications: str
    delai_livraison: int
    penalites_retard: float


class CahierChargesCreate(CahierChargesBase):
    normes: str = ""
    conditions_commerciales: str = ""
    conditions_paiement: str = ""
    garanties: str = ""
    clauses_speciales: str = ""


class CahierChargesUpdate(BaseModel):
    statut: Optional[str] = None
    normes: Optional[str] = None
    conditions_commerciales: Optional[str] = None
    conditions_paiement: Optional[str] = None
    garanties: Optional[str] = None
    clauses_speciales: Optional[str] = None
    approuve_par: Optional[str] = None
    date_approbation: Optional[date] = None


class CahierChargesResponse(CahierChargesBase):
    id: int
    version: int
    date_version: date
    devise: str
    normes: Optional[str] = None
    conditions_commerciales: Optional[str] = None
    conditions_paiement: Optional[str] = None
    garanties: Optional[str] = None
    clauses_speciales: Optional[str] = None
    approuve_par: Optional[str] = None
    date_approbation: Optional[date] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne CDC schemas
class LigneCDCBase(BaseModel):
    cdc_id: int
    article_id: int
    designation: str
    quantite: float
    unite: str
    specifications_detaillees: str
    budget_unitaire: float
    priorite: str


class LigneCDCCreate(LigneCDCBase):
    norme: str = ""
    classe: str = ""
    origine: str = "local"


class LigneCDCUpdate(BaseModel):
    norme: Optional[str] = None
    classe: Optional[str] = None
    origine: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class LigneCDCResponse(LigneCDCBase):
    id: int
    budget_total: float
    devise: str
    norme: Optional[str] = None
    classe: Optional[str] = None
    origine: Optional[str] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Offre schemas
class OffreBase(BaseModel):
    numero_offre: str
    appel_offres_id: int
    fournisseur_id: int
    montant_total: float
    delai_livraison: int
    validite_offre: int


class OffreCreate(OffreBase):
    notes: str = ""


class OffreUpdate(BaseModel):
    statut: Optional[str] = None
    raison_rejet: Optional[str] = None
    rang: Optional[int] = None
    notes: Optional[str] = None


class OffreResponse(OffreBase):
    id: int
    devise: str
    date_reception: date
    date_validite: date
    notes: Optional[str] = None
    statut: str
    raison_rejet: Optional[str] = None
    rang: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne Offre schemas
class LigneOffreBase(BaseModel):
    offre_id: int
    ligne_cdc_id: int
    designation: str
    quantite: float
    unite: str
    prix_unitaire: float


class LigneOffreCreate(LigneOffreBase):
    delai: int = 30
    conformite: bool = True
    observations: str = ""


class LigneOffreUpdate(BaseModel):
    delai: Optional[int] = None
    conformite: Optional[bool] = None
    observations: Optional[str] = None


class LigneOffreResponse(LigneOffreBase):
    id: int
    prix_total: float
    devise: str
    delai: int
    conformite: bool
    observations: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Evaluation Offre schemas
class EvaluationOffreBase(BaseModel):
    offre_id: int
    critere: str
    note: float
    poids: float


class EvaluationOffreCreate(EvaluationOffreBase):
    evaluateur: str
    commentaires: str = ""


class EvaluationOffreResponse(EvaluationOffreBase):
    id: int
    note_ponderee: float
    evaluateur: str
    date_evaluation: date
    commentaires: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Comparatif schemas
class ComparatifBase(BaseModel):
    numero_comparatif: str
    appel_offres_id: int
    cree_par: str


class ComparatifCreate(ComparatifBase):
    pass


class ComparatifUpdate(BaseModel):
    date_cloture: Optional[date] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    statut: Optional[str] = None
    conclusions: Optional[str] = None
    recommandation: Optional[str] = None


class ComparatifResponse(ComparatifBase):
    id: int
    date_creation: date
    date_cloture: Optional[date] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    statut: str
    conclusions: Optional[str] = None
    recommandation: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne Comparatif schemas
class LigneComparatifBase(BaseModel):
    comparatif_id: int
    fournisseur_id: int
    offre_id: int
    ligne_cdc_id: int
    prix: float
    delai: int
    note_qualite: float
    note_technique: float
    note_financiere: float


class LigneComparatifCreate(LigneComparatifBase):
    pass


class LigneComparatifResponse(LigneComparatifBase):
    id: int
    devise: str
    note_globale: float
    rang: Optional[int] = None
    qualite: Optional[str] = None
    observations: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Contrat Cadre schemas
class ContratCadreBase(BaseModel):
    numero_contrat: str
    fournisseur_id: int
    type_contrat: str
    date_signature: date
    date_debut: date
    date_fin: date
    montant_annuel: float


class ContratCadreCreate(ContratCadreBase):
    conditions_renouvellement: str = ""
    conditions_resiliation: str = ""
    garanties: str = ""
    clauses_speciales: str = ""


class ContratCadreUpdate(BaseModel):
    statut: Optional[str] = None
    conditions_renouvellement: Optional[str] = None
    conditions_resiliation: Optional[str] = None
    garanties: Optional[str] = None
    clauses_speciales: Optional[str] = None


class ContratCadreResponse(ContratCadreBase):
    id: int
    devise: str
    duree_mois: int
    conditions_renouvellement: Optional[str] = None
    conditions_resiliation: Optional[str] = None
    garanties: Optional[str] = None
    clauses_speciales: Optional[str] = None
    signe_par: Optional[str] = None
    fonction: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Bon Commande schemas
class BonCommandeBase(BaseModel):
    numero_bc: str
    fournisseur_id: int
    date_prevue_livraison: date
    destinataire: str
    lieu_livraison: str
    conditions_paiement: str


class BonCommandeCreate(BonCommandeBase):
    contrat_cadre_id: Optional[int] = None
    notes: str = ""


class BonCommandeUpdate(BaseModel):
    contrat_cadre_id: Optional[int] = None
    date_reelle_livraison: Optional[date] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None


class BonCommandeResponse(BonCommandeBase):
    id: int
    contrat_cadre_id: Optional[int] = None
    date_creation: date
    date_reelle_livraison: Optional[date] = None
    devise: str
    montant_total: Optional[float] = None
    statut: str
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne BC schemas
class LigneBCBase(BaseModel):
    bc_id: int
    article_id: int
    designation: str
    quantite: float
    unite: str
    prix_unitaire: float


class LigneBCCreate(LigneBCBase):
    pass


class LigneBCUpdate(BaseModel):
    quantite_recue: Optional[float] = None
    date_reception: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class LigneBCResponse(LigneBCBase):
    id: int
    prix_total: float
    devise: str
    quantite_recue: float
    date_reception: Optional[date] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Reception schemas
class ReceptionBase(BaseModel):
    numero_reception: str
    bc_id: int
    fournisseur_id: int
    type_reception: str
    lieu_reception: str
    responsable: str


class ReceptionCreate(ReceptionBase):
    date_prevue: Optional[date] = None
    transporteur: str = ""
    numero_transport: str = ""
    nombre_colis: int = 0
    poids_brut: float = 0.0
    poids_net: float = 0.0
    emballage: str = ""
    notes: str = ""


class ReceptionUpdate(BaseModel):
    date_reelle: Optional[date] = None
    condition_marchandise: Optional[str] = None
    statut: Optional[str] = None
    controle_qualite: Optional[bool] = None
    date_controle: Optional[date] = None
    controle_par: Optional[str] = None
    photo: Optional[str] = None
    notes: Optional[str] = None


class ReceptionResponse(ReceptionBase):
    id: int
    date_prevue: Optional[date] = None
    date_reception: date
    transporteur: Optional[str] = None
    numero_transport: Optional[str] = None
    nombre_colis: int
    poids_brut: float
    poids_net: float
    emballage: Optional[str] = None
    condition_marchandise: str
    statut: str
    controle_qualite: bool
    date_controle: Optional[date] = None
    controle_par: Optional[str] = None
    photo: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne Reception schemas
class LigneReceptionBase(BaseModel):
    reception_id: int
    ligne_bc_id: int
    article_id: int
    designation: str
    quantite_commandee: float
    quantite_recue: float
    quantite_acceptee: float
    quantite_refusee: float
    unite: str
    prix_unitaire: float


class LigneReceptionCreate(LigneReceptionBase):
    conformite: bool = True
    motif_refus: str = ""
    etat: str = "neuf"
    emplacement: str = ""
    date_peremption: Optional[date] = None
    numero_lot: str = ""


class LigneReceptionUpdate(BaseModel):
    conformite: Optional[bool] = None
    motif_refus: Optional[str] = None
    etat: Optional[str] = None
    emplacement: Optional[str] = None
    statut: Optional[str] = None


class LigneReceptionResponse(LigneReceptionBase):
    id: int
    valeur_recue: float
    devise: str
    conformite: bool
    motif_refus: Optional[str] = None
    etat: str
    emplacement: Optional[str] = None
    date_peremption: Optional[date] = None
    numero_lot: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Litige Fournisseur schemas
class LitigeFournisseurBase(BaseModel):
    numero_litige: str
    fournisseur_id: int
    type_litige: str
    description: str
    gravite: str
    montant_en_litige: float


class LitigeFournisseurCreate(LitigeFournisseurBase):
    bc_id: Optional[int] = None
    reception_id: Optional[int] = None
    mesure_demandee: str = ""


class LitigeFournisseurUpdate(BaseModel):
    statut: Optional[str] = None
    date_cloture: Optional[date] = None
    resolution: Optional[str] = None
    responsable: Optional[str] = None


class LitigeFournisseurResponse(LitigeFournisseurBase):
    id: int
    devise: str
    bc_id: Optional[int] = None
    reception_id: Optional[int] = None
    date_ouverture: date
    mesure_demandee: Optional[str] = None
    date_cloture: Optional[date] = None
    resolution: Optional[str] = None
    statut: str
    responsable: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Historique Litige schemas
class HistoriqueLitigeBase(BaseModel):
    litige_id: int
    action: str
    description: str
    auteur: str
    resultat: str


class HistoriqueLitigeCreate(HistoriqueLitigeBase):
    pass


class HistoriqueLitigeResponse(HistoriqueLitigeBase):
    id: int
    date_action: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Evaluation Fournisseur schemas
class EvaluationFournisseurBase(BaseModel):
    fournisseur_id: int
    periode: str
    note_qualite: float
    note_delai: float
    note_prix: float
    note_service: float


class EvaluationFournisseurCreate(EvaluationFournisseurBase):
    evaluateur: str
    commentaires: str = ""
    recommandation: str = ""


class EvaluationFournisseurUpdate(BaseModel):
    recommandation: Optional[str] = None
    commentaires: Optional[str] = None


class EvaluationFournisseurResponse(EvaluationFournisseurBase):
    id: int
    date_evaluation: date
    evaluateur: str
    note_globale: float
    classement: str
    commentaires: Optional[str] = None
    recommandation: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapport Fournisseur
class RapportFournisseurResponse(BaseModel):
    fournisseur_id: int
    evaluations: dict
    contrats: dict
    litiges: dict
