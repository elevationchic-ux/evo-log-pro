"""Pydantic schemas for RH module"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# Conge schemas
class CongeBase(BaseModel):
    type_conge: str = Field(..., description="Type de congé: annuel, maladie, exceptionnel")
    date_debut: date
    date_fin: date
    motif: str


class CongeCreate(CongeBase):
    pass


class CongeUpdate(BaseModel):
    statut: Optional[str] = None
    approbateur_id: Optional[int] = None
    date_approbation: Optional[datetime] = None
    commentaire_approbation: Optional[str] = None
    motif_refus: Optional[str] = None


class CongeResponse(CongeBase):
    id: int
    employe_id: int
    nombre_jours: int
    statut: str
    date_demande: datetime
    approbateur_id: Optional[int] = None
    date_approbation: Optional[datetime] = None
    commentaire_approbation: Optional[str] = None
    motif_refus: Optional[str] = None
    
    class Config:
        from_attributes = True


class SoldeCongeResponse(BaseModel):
    solde: float
    utilise: float
    reste: float
    annee: int


# Absence schemas
class AbsenceBase(BaseModel):
    type_absence: str = Field(..., description="Type d'absence: maladie, familiale, autre")
    date_debut: date
    date_fin: date
    motif: str
    justifie: bool = False


class AbsenceCreate(AbsenceBase):
    pass


class AbsenceUpdate(BaseModel):
    justifie: Optional[bool] = None
    motif: Optional[str] = None


class AbsenceResponse(AbsenceBase):
    id: int
    employe_id: int
    nombre_jours: int
    date_enregistrement: datetime
    
    class Config:
        from_attributes = True


# TempsTravail schemas
class TempsTravailBase(BaseModel):
    date: date
    heure_arrivee: datetime
    heure_depart: Optional[datetime] = None
    statut: str = "present"


class TempsTravailCreate(TempsTravailBase):
    pass


class TempsTravailUpdate(BaseModel):
    heure_depart: Optional[datetime] = None
    statut: Optional[str] = None


class TempsTravailResponse(TempsTravailBase):
    id: int
    employe_id: int
    heures_travaillees: Optional[float] = None
    heures_sup: Optional[float] = None
    
    class Config:
        from_attributes = True


class HeuresMensuellesResponse(BaseModel):
    heures_travaillees: float
    heures_sup: float
    jours_presents: int


# Formation schemas
class FormationBase(BaseModel):
    titre: str
    description: str
    date_debut: date
    date_fin: date
    duree_heures: int
    cout: float
    formateur: str
    lieu: str


class FormationCreate(FormationBase):
    agency_id: Optional[int] = None


class FormationUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    certificat_valide_jusque: Optional[date] = None


class FormationResponse(FormationBase):
    id: int
    agency_id: Optional[int] = None
    statut: str
    certificat_valide_jusque: Optional[date] = None
    
    class Config:
        from_attributes = True


class ParticipationFormationBase(BaseModel):
    formation_id: int
    employe_id: int


class ParticipationFormationCreate(ParticipationFormationBase):
    pass


class ParticipationFormationUpdate(BaseModel):
    present: Optional[bool] = None
    certificat_obtenu: Optional[bool] = None
    commentaire: Optional[str] = None
    statut: Optional[str] = None


class ParticipationFormationResponse(ParticipationFormationBase):
    id: int
    date_inscription: datetime
    present: Optional[bool] = None
    certificat_obtenu: Optional[bool] = None
    commentaire: Optional[str] = None
    statut: str
    
    class Config:
        from_attributes = True


# EvaluationPerformance schemas
class EvaluationPerformanceBase(BaseModel):
    periode_debut: date
    periode_fin: date
    note_globale: float = Field(..., ge=0, le=5)
    commentaires: str
    objectifs_atteints: int
    objectifs_total: int


class EvaluationPerformanceCreate(EvaluationPerformanceBase):
    employe_id: int
    evaluateur_id: int


class EvaluationPerformanceUpdate(BaseModel):
    note_globale: Optional[float] = None
    commentaires: Optional[str] = None


class EvaluationPerformanceResponse(EvaluationPerformanceBase):
    id: int
    employe_id: int
    evaluateur_id: int
    date_evaluation: datetime
    
    class Config:
        from_attributes = True


# ContratTravail schemas
class ContratTravailBase(BaseModel):
    type_contrat: str = Field(..., description="CDI, CDD, Stage")
    date_debut: date
    date_fin: Optional[date] = None
    poste: str
    salaire_base: float
    coefficient: Optional[int] = None
    classification: Optional[str] = None
    periode_essai_jours: int = 90


class ContratTravailCreate(ContratTravailBase):
    employe_id: int


class ContratTravailUpdate(BaseModel):
    date_fin: Optional[date] = None
    salaire_base: Optional[float] = None
    statut: Optional[str] = None


class ContratTravailResponse(ContratTravailBase):
    id: int
    employe_id: int
    statut: str
    nombre_renouvellements: Optional[int] = None
    date_dernier_renouvellement: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Salaire schemas
class SalaireBase(BaseModel):
    mois: int
    annee: int
    salaire_brut: float
    salaire_net: float
    heures_sup: float = 0
    primes: float = 0
    deductions: float = 0


class SalaireCreate(SalaireBase):
    employe_id: int


class SalaireResponse(SalaireBase):
    id: int
    employe_id: int
    date_paiement: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Prime schemas
class PrimeBase(BaseModel):
    type_prime: str
    montant: float
    motif: str
    date_prime: date


class PrimeCreate(PrimeBase):
    employe_id: int


class PrimeResponse(PrimeBase):
    id: int
    employe_id: int
    
    class Config:
        from_attributes = True


# DocumentEmploye schemas
class DocumentEmployeBase(BaseModel):
    type_document: str
    chemin_fichier: str
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None


class DocumentEmployeCreate(DocumentEmployeBase):
    employe_id: int


class DocumentEmployeUpdate(BaseModel):
    date_expiration: Optional[date] = None
    chemin_fichier: Optional[str] = None


class DocumentEmployeResponse(DocumentEmployeBase):
    id: int
    employe_id: int
    date_ajout: datetime
    
    class Config:
        from_attributes = True


# Organigramme schemas
class OrganigrammeBase(BaseModel):
    manager_id: Optional[int] = None
    departement: str
    poste: str


class OrganigrammeCreate(OrganigrammeBase):
    employe_id: int


class OrganigrammeUpdate(OrganigrammeBase):
    pass


class OrganigrammeResponse(OrganigrammeBase):
    id: int
    employe_id: int
    date_creation: Optional[datetime] = None
    date_mise_a_jour: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Competence schemas
class CompetenceBase(BaseModel):
    nom: str
    categorie: str
    description: str
    niveau_requis: str


class CompetenceCreate(CompetenceBase):
    pass


class CompetenceUpdate(BaseModel):
    description: Optional[str] = None
    niveau_requis: Optional[str] = None


class CompetenceResponse(CompetenceBase):
    id: int
    
    class Config:
        from_attributes = True


class CompetenceEmployeBase(BaseModel):
    competence_id: int
    niveau: str
    date_evaluation: Optional[date] = None


class CompetenceEmployeCreate(CompetenceEmployeBase):
    employe_id: int


class CompetenceEmployeUpdate(BaseModel):
    niveau: Optional[str] = None


class CompetenceEmployeResponse(CompetenceEmployeBase):
    id: int
    employe_id: int
    
    class Config:
        from_attributes = True


# Payroll bulletin schema
class BulletinPaieResponse(BaseModel):
    employe_id: int
    periode: str
    salaire_base: float
    heures_sup: float
    indemnite_heures_sup: float
    primes: List[dict]
    total_primes: float
    salaire_brut: float
    cotisations: dict
    impot_revenu: float
    deductions: List[dict]
    total_deductions: float
    salaire_net: float
    note: str
