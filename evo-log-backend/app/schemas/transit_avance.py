"""Pydantic schemas for Transit Avancé module - Complete customs operations"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# Bureau Douane schemas
class BureauDouaneBase(BaseModel):
    code: str
    nom: str
    type_bureau: str
    port_id: int
    region: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    horaires: Optional[str] = None


class BureauDouaneCreate(BureauDouaneBase):
    pass


class BureauDouaneUpdate(BaseModel):
    statut: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    horaires: Optional[str] = None


class BureauDouaneResponse(BureauDouaneBase):
    id: int
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Dossier Transit Avance schemas
class DossierTransitAvanceBase(BaseModel):
    numero_dossier: str
    client_id: int
    transitaire_id: int
    type_transit: str
    regime_douanier: str
    bureau_entree_id: int
    bureau_sortie_id: int
    marchandise: str
    valeur_marchandise: float
    pays_origine_code: str
    pays_destination_code: str


class DossierTransitAvanceCreate(DossierTransitAvanceBase):
    pass


class DossierTransitAvanceUpdate(BaseModel):
    statut: Optional[str] = None
    poids_brut: Optional[float] = None
    poids_net: Optional[float] = None
    nombre_colis: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    moyen_transport: Optional[str] = None
    numero_connaisse: Optional[str] = None
    numero_cmr: Optional[str] = None
    numero_tir: Optional[str] = None
    correspondant_agree: Optional[str] = None
    reference_sygdonia: Optional[str] = None
    notes: Optional[str] = None


class DossierTransitAvanceResponse(DossierTransitAvanceBase):
    id: int
    devise: str
    poids_brut: Optional[float] = None
    poids_net: Optional[float] = None
    nombre_colis: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    moyen_transport: Optional[str] = None
    numero_connaisse: Optional[str] = None
    numero_cmr: Optional[str] = None
    numero_tir: Optional[str] = None
    taux_change: float
    montant_frais: Optional[float] = None
    montant_droits: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_total: Optional[float] = None
    correspondant_agree: Optional[str] = None
    reference_sygdonia: Optional[str] = None
    statut: str
    date_ouverture: datetime
    date_cloture: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Visite Physique schemas
class VisitePhysiqueBase(BaseModel):
    dossier_transit_id: int
    inspecteur_id: int
    type_visite: str
    rapport: str


class VisitePhysiqueCreate(VisitePhysiqueBase):
    prelevement: bool = False
    echantillon: Optional[str] = None


class VisitePhysiqueUpdate(BaseModel):
    resultat: Optional[str] = None
    conformite: Optional[bool] = None
    observations: Optional[str] = None
    photos: Optional[str] = None


class VisitePhysiqueResponse(VisitePhysiqueBase):
    id: int
    date_visite: datetime
    prelevement: bool
    echantillon: Optional[str] = None
    resultat: str
    conformite: bool
    observations: Optional[str] = None
    photos: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Valorisation Douaniere schemas
class ValorisationDouaniereBase(BaseModel):
    dossier_transit_id: int
    methode_valorisation: str
    valeur_caf: float
    fret: float
    assurance: float
    autres_frais: float
    taux_change: float
    valide_par: int


class ValorisationDouaniereCreate(ValorisationDouaniereBase):
    pass


class ValorisationDouaniereResponse(ValorisationDouaniereBase):
    id: int
    valeur_fob: float
    devise: str
    date_valorisation: date
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Nomenclature CEMAC schemas
class NomenclatureCEMACBase(BaseModel):
    code_hs: str
    description: str
    section: str
    chapitre: str
    position: str
    taux_dd: float
    taux_tva: float
    unite: Optional[str] = None
    pays_origine: Optional[str] = None
    restrictions: Optional[str] = None


class NomenclatureCEMACCreate(NomenclatureCEMACBase):
    pass


class NomenclatureCEMACUpdate(BaseModel):
    taux_dd: Optional[float] = None
    taux_tva: Optional[float] = None
    restrictions: Optional[str] = None
    statut: Optional[str] = None


class NomenclatureCEMACResponse(NomenclatureCEMACBase):
    id: int
    statut: str
    date_effet: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Declaration Douaniere Avance schemas
class DeclarationDouaniereAvanceBase(BaseModel):
    numero_declaration: str
    dossier_transit_id: int
    regime_douanier: str
    bureau_douane_id: int
    valeur_declaree: float
    code_hs: str


class DeclarationDouaniereAvanceCreate(DeclarationDouaniereAvanceBase):
    pass


class DeclarationDouaniereAvanceUpdate(BaseModel):
    statut: Optional[str] = None
    reference_sygdonia: Optional[str] = None
    numero_b7: Optional[str] = None
    numero_quitus: Optional[str] = None
    certificat_origine: Optional[str] = None
    facture_proforma: Optional[str] = None
    facture_commerciale: Optional[str] = None
    motifs_rejet: Optional[str] = None
    notes: Optional[str] = None


class DeclarationDouaniereAvanceResponse(DeclarationDouaniereAvanceBase):
    id: int
    devise: str
    poids_declare: Optional[float] = None
    taux_dd: float
    montant_dd: float
    taux_tva: float
    montant_tva: float
    taux_autres_taxes: Optional[float] = None
    montant_autres_taxes: Optional[float] = None
    total_taxes: float
    numero_b7: Optional[str] = None
    numero_quitus: Optional[str] = None
    statut: str
    reference_sygdonia: Optional[str] = None
    date_enregistrement: Optional[datetime] = None
    date_validation: Optional[datetime] = None
    date_acquittement: Optional[datetime] = None
    certificat_origine: Optional[str] = None
    facture_proforma: Optional[str] = None
    facture_commerciale: Optional[str] = None
    motifs_rejet: Optional[str] = None
    date_rejet: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne Declaration schemas
class LigneDeclarationBase(BaseModel):
    declaration_id: int
    numero_ligne: int
    designation: str
    quantite: float
    unite: str
    poids_net: float
    poids_brut: float
    valeur_unitaire: float
    code_hs: str


class LigneDeclarationCreate(LigneDeclarationBase):
    pass


class LigneDeclarationResponse(LigneDeclarationBase):
    id: int
    valeur_totale: float
    taux_dd: float
    montant_dd: float
    taux_tva: float
    montant_tva: float
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bon AD schemas
class BonADBase(BaseModel):
    numero_bad: str
    dossier_transit_id: int
    signataire: str
    qualite: str


class BonADCreate(BonADBase):
    declaration_id: Optional[int] = None


class BonADUpdate(BaseModel):
    statut: Optional[str] = None
    reference_sygdonia: Optional[str] = None
    numero_quitus: Optional[str] = None
    notes: Optional[str] = None


class BonADResponse(BonADBase):
    id: int
    declaration_id: Optional[int] = None
    date_signature: date
    statut: str
    reference_sygdonia: Optional[str] = None
    numero_quitus: Optional[str] = None
    montant_total: Optional[float] = None
    devise: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# AMC schemas
class AvisMiseConsommationBase(BaseModel):
    numero_amc: str
    dossier_transit_id: int
    bureau_douane_id: int
    valide_par: str
    fonction: str


class AvisMiseConsommationCreate(AvisMiseConsommationBase):
    declaration_id: Optional[int] = None


class AvisMiseConsommationUpdate(BaseModel):
    statut: Optional[str] = None
    notes: Optional[str] = None


class AvisMiseConsommationResponse(AvisMiseConsommationBase):
    id: int
    declaration_id: Optional[int] = None
    date_emission: date
    date_validite: date
    date_limite: date
    montant_dd: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_total: Optional[float] = None
    devise: str
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Credit Enlevement schemas
class CreditEnlevementBase(BaseModel):
    numero_credit: str
    dossier_transit_id: int
    type_garantie: str
    garant: str
    montant_garantie: float
    date_echeance: date


class CreditEnlevementCreate(CreditEnlevementBase):
    pass


class CreditEnlevementUpdate(BaseModel):
    statut: Optional[str] = None
    reference_sygdonia: Optional[str] = None
    notes: Optional[str] = None


class CreditEnlevementResponse(CreditEnlevementBase):
    id: int
    devise: str
    date_delivrance: date
    statut: str
    reference_sygdonia: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Droit Port schemas
class DroitPortBase(BaseModel):
    dossier_transit_id: int
    type_droit: str
    description: str
    base_calcul: str
    quantite: float
    taux: float


class DroitPortCreate(DroitPortBase):
    pass


class DroitPortUpdate(BaseModel):
    statut: Optional[str] = None
    reference_facture: Optional[str] = None


class DroitPortResponse(DroitPortBase):
    id: int
    montant: float
    devise: str
    date_facturation: date
    reference_facture: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Timbre Usage schemas
class TimbreUsageBase(BaseModel):
    dossier_transit_id: int
    type_timbre: str
    montant: float
    numero_timbre: str


class TimbreUsageCreate(TimbreUsageBase):
    pass


class TimbreUsageUpdate(BaseModel):
    statut: Optional[str] = None


class TimbreUsageResponse(TimbreUsageBase):
    id: int
    devise: str
    date_apposition: date
    statut: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Litige Douanier schemas
class LitigeDouanierBase(BaseModel):
    dossier_transit_id: int
    type_litige: str
    description: str
    montant_en_litige: float


class LitigeDouanierCreate(LitigeDouanierBase):
    pass


class LitigeDouanierUpdate(BaseModel):
    statut: Optional[str] = None
    decision: Optional[str] = None
    date_decision: Optional[datetime] = None
    recours: Optional[str] = None
    notes: Optional[str] = None


class LitigeDouanierResponse(LitigeDouanierBase):
    id: int
    devise: str
    date_litige: datetime
    statut: str
    decision: Optional[str] = None
    date_decision: Optional[datetime] = None
    recours: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Archivage Dossier schemas
class ArchivageDossierBase(BaseModel):
    dossier_transit_id: int
    lieu_archivage: str
    numero_archive: str
    contenu: str


class ArchivageDossierCreate(ArchivageDossierBase):
    pass


class ArchivageDossierUpdate(BaseModel):
    accessible: Optional[bool] = None


class ArchivageDossierResponse(ArchivageDossierBase):
    id: int
    date_archivage: date
    date_destruction: date
    statut: str
    accessible: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Procedure Urgente schemas
class ProcedureUrgenteBase(BaseModel):
    dossier_transit_id: int
    type_urgence: str
    justification: str


class ProcedureUrgenteCreate(ProcedureUrgenteBase):
    pass


class ProcedureUrgenteUpdate(BaseModel):
    statut: Optional[str] = None
    autorise_par: Optional[str] = None
    fonction: Optional[str] = None
    notes: Optional[str] = None


class ProcedureUrgenteResponse(ProcedureUrgenteBase):
    id: int
    date_demande: datetime
    date_autorisation: Optional[datetime] = None
    autorise_par: Optional[str] = None
    fonction: Optional[str] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapport Dossier
class RapportDossierResponse(BaseModel):
    dossier: dict
    declarations: dict
    visites: dict
