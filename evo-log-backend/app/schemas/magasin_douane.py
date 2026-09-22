"""Pydantic schemas for Magasin Douane module - Warehouse under customs"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Entrepot Douane schemas
class EntrepotDouaneBase(BaseModel):
    code: str
    nom: str
    type_entrepot: str
    regime: str
    adresse: str
    surface_m2: float
    capacite_tonnage: float
    numero_agrement: str
    date_agrement: date
    date_expiration_agrement: date


class EntrepotDouaneCreate(EntrepotDouaneBase):
    temperature_controlee: bool = False
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    controle_humidite: bool = False
    zone_dangereuse: bool = False
    equipe_surveillance: Optional[str] = None
    garde_agree: Optional[str] = None


class EntrepotDouaneUpdate(BaseModel):
    statut: Optional[str] = None
    equipe_surveillance: Optional[str] = None
    garde_agree: Optional[str] = None


class EntrepotDouaneResponse(EntrepotDouaneBase):
    id: int
    temperature_controlee: bool
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    controle_humidite: bool
    zone_dangereuse: bool
    equipe_surveillance: Optional[str] = None
    garde_agree: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Declaration Entrepot schemas
class DeclarationEntrepotBase(BaseModel):
    numero_declaration: str
    entrepot_id: int
    dossier_transit_id: int
    regime: str
    valeur_marchandise: float


class DeclarationEntrepotCreate(DeclarationEntrepotBase):
    pass


class DeclarationEntrepotUpdate(BaseModel):
    statut: Optional[str] = None
    date_acceptation: Optional[date] = None
    date_limite: Optional[date] = None
    valide_par: Optional[str] = None
    fonction: Optional[str] = None
    reference_sygdonia: Optional[str] = None
    motifs_refus: Optional[str] = None
    notes: Optional[str] = None


class DeclarationEntrepotResponse(DeclarationEntrepotBase):
    id: int
    devise: str
    date_declaration: date
    date_acceptation: Optional[date] = None
    date_limite: Optional[date] = None
    valide_par: Optional[str] = None
    fonction: Optional[str] = None
    reference_sygdonia: Optional[str] = None
    statut: str
    motifs_refus: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne Entrepot schemas
class LigneEntrepotBase(BaseModel):
    declaration_id: int
    article_id: int
    designation: str
    quantite: float
    unite: str
    poids_net: float
    poids_brut: float
    valeur_unitaire: float
    emplacement: str
    numero_lot: str


class LigneEntrepotCreate(LigneEntrepotBase):
    date_peremption: Optional[date] = None
    dangereux: bool = False
    classe_imdg: Optional[str] = None


class LigneEntrepotUpdate(BaseModel):
    statut: Optional[str] = None
    date_sortie: Optional[date] = None
    motif_sortie: Optional[str] = None
    notes: Optional[str] = None


class LigneEntrepotResponse(LigneEntrepotBase):
    id: int
    valeur_totale: float
    date_peremption: Optional[date] = None
    dangereux: bool
    classe_imdg: Optional[str] = None
    statut: str
    date_sortie: Optional[date] = None
    motif_sortie: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Fiche Magasin schemas
class FicheMagasinBase(BaseModel):
    numero_fiche: str
    entrepot_id: int
    article_id: int
    designation: str
    numero_lot: str
    stock_initial: float
    unite: str
    emplacement: str
    valeur_unitaire: float


class FicheMagasinCreate(FicheMagasinBase):
    pass


class FicheMagasinUpdate(BaseModel):
    stock_actuel: Optional[float] = None
    derniere_mouvement: Optional[datetime] = None
    statut: Optional[str] = None


class FicheMagasinResponse(FicheMagasinBase):
    id: int
    date_creation: date
    stock_actuel: float
    valeur_totale: float
    derniere_mouvement: Optional[datetime] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Mouvement Fiche schemas
class MouvementFicheBase(BaseModel):
    fiche_id: int
    type_mouvement: str
    quantite: float
    type_operation: str
    document_reference: str
    operateur: str


class MouvementFicheCreate(MouvementFicheBase):
    motif: str = ""
    numero_declaration: Optional[str] = None


class MouvementFicheResponse(MouvementFicheBase):
    id: int
    date_mouvement: datetime
    stock_apres: float
    numero_declaration: Optional[str] = None
    motif: str
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventaire Douanier schemas
class InventaireDouanierBase(BaseModel):
    numero_inventaire: str
    entrepot_id: int
    type_inventaire: str
    operateur: str


class InventaireDouanierCreate(InventaireDouanierBase):
    pass


class InventaireDouanierUpdate(BaseModel):
    date_fin: Optional[date] = None
    inspecteur_douane: Optional[str] = None
    date_inspection: Optional[datetime] = None
    resultat: Optional[str] = None
    ecart_tonnage: Optional[float] = None
    ecart_valeur: Optional[float] = None
    motif_ecart: Optional[str] = None
    measures_correctives: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class InventaireDouanierResponse(InventaireDouanierBase):
    id: int
    date_debut: date
    date_fin: Optional[date] = None
    inspecteur_douane: Optional[str] = None
    date_inspection: Optional[datetime] = None
    resultat: Optional[str] = None
    ecart_tonnage: Optional[float] = None
    ecart_valeur: Optional[float] = None
    motif_ecart: Optional[str] = None
    measures_correctives: Optional[str] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne Inventaire Douanier schemas
class LigneInventaireDouanierBase(BaseModel):
    inventaire_id: int
    article_id: int
    designation: str
    numero_lot: str
    emplacement: str
    stock_theorique: float
    stock_reel: float
    unite: str
    valeur_unitaire: float


class LigneInventaireDouanierCreate(LigneInventaireDouanierBase):
    date_peremption: Optional[date] = None


class LigneInventaireDouanierResponse(LigneInventaireDouanierBase):
    id: int
    ecart: float
    valeur_ecart: float
    date_peremption: Optional[date] = None
    conforme: bool
    motif_ecart: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Surveillance Magazin schemas
class SurveillanceMagazinBase(BaseModel):
    entrepot_id: int
    gardien: str
    type_controle: str
    zones_controlees: str


class SurveillanceMagazinCreate(SurveillanceMagazinBase):
    incidents: str = ""
    anomalies: str = ""
    photos: str = ""


class SurveillanceMagazinUpdate(BaseModel):
    statut: Optional[str] = None
    mesure_prise: Optional[str] = None
    notes: Optional[str] = None


class SurveillanceMagazinResponse(SurveillanceMagazinBase):
    id: int
    date_patrouille: datetime
    incidents: str
    anomalies: str
    statut: str
    mesure_prise: Optional[str] = None
    photos: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Mise Consommation schemas
class MiseConsommationBase(BaseModel):
    numero_mise: str
    declaration_entrepot_id: int
    valide_par: str
    fonction: str


class MiseConsommationCreate(MiseConsommationBase):
    pass


class MiseConsommationUpdate(BaseModel):
    reference_sygdonia: Optional[str] = None
    montant_dd: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_total: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class MiseConsommationResponse(MiseConsommationBase):
    id: int
    date_mise: date
    reference_sygdonia: Optional[str] = None
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


# Reexportation schemas
class ReexportationBase(BaseModel):
    numero_reexport: str
    declaration_entrepot_id: int
    pays_destination: str
    code_pays_destination: str
    motif: str
    moyen_transport: str


class ReexportationCreate(ReexportationBase):
    pass


class ReexportationUpdate(BaseModel):
    reference_sygdonia: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class ReexportationResponse(ReexportationBase):
    id: int
    date_reexport: date
    reference_sygdonia: Optional[str] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Destruction schemas
class DestructionBase(BaseModel):
    numero_destruction: str
    declaration_entrepot_id: int
    motif: str
    type_destruction: str


class DestructionCreate(DestructionBase):
    pass


class DestructionUpdate(BaseModel):
    date_autorisation: Optional[date] = None
    autorise_par: Optional[str] = None
    fonction: Optional[str] = None
    temoin: Optional[str] = None
    date_destruction: Optional[date] = None
    poids_destruct: Optional[float] = None
    valeur_destruct: Optional[float] = None
    rapport_destruction: Optional[str] = None
    photos: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class DestructionResponse(DestructionBase):
    id: int
    date_demande: date
    date_autorisation: Optional[date] = None
    autorise_par: Optional[str] = None
    fonction: Optional[str] = None
    temoin: Optional[str] = None
    date_destruction: Optional[date] = None
    poids_destruct: Optional[float] = None
    valeur_destruct: Optional[float] = None
    devise: str
    rapport_destruction: Optional[str] = None
    photos: Optional[str] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Entretien Stock schemas
class EntretienStockBase(BaseModel):
    numero_entretien: str
    declaration_entrepot_id: int
    type_entretien: str
    article_id: int
    quantite: float
    unite: str
    operateur: str
    description: str


class EntretienStockCreate(EntretienStockBase):
    pass


class EntretienStockUpdate(BaseModel):
    autorise_par: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class EntretienStockResponse(EntretienStockBase):
    id: int
    date_entretien: date
    autorise_par: Optional[str] = None
    statut: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Assurance Stock schemas
class AssuranceStockBase(BaseModel):
    entrepot_id: int
    numero_police: str
    assureur: str
    type_couverture: str
    valeur_assuree: float
    prime_annuelle: float
    date_debut: date
    date_fin: date
    franchise: float


class AssuranceStockCreate(AssuranceStockBase):
    exclusions: str = ""


class AssuranceStockUpdate(BaseModel):
    statut: Optional[str] = None
    exclusions: Optional[str] = None


class AssuranceStockResponse(AssuranceStockBase):
    id: int
    devise: str
    exclusions: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Compte Rendu Manutention schemas
class CompteRenduManutentionBase(BaseModel):
    numero_cr: str
    entrepot_id: int
    type_operation: str
    equipe: str
    equipement: str
    duree_heures: float
    nombre_mouvements: int
    tonnage_total: float


class CompteRenduManutentionCreate(CompteRenduManutentionBase):
    observations: str = ""


class CompteRenduManutentionUpdate(BaseModel):
    observations: Optional[str] = None
    controle_par: Optional[int] = None
    date_controle: Optional[datetime] = None
    conforme: Optional[bool] = None


class CompteRenduManutentionResponse(CompteRenduManutentionBase):
    id: int
    date_operation: date
    observations: Optional[str] = None
    controle_par: Optional[int] = None
    date_controle: Optional[datetime] = None
    conforme: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Rapport Entrepot
class RapportEntrepotResponse(BaseModel):
    entrepot: dict
    stock: dict
    declarations: dict
