"""Schemas Pydantic pour portail-declarant (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class DeclCustomsDeclarationCreate(BaseModel):
    reference: str
    masse: Optional[str] = None
    regime: Optional[str] = None
    valeur_douane: Optional[float] = None
    date_depot: Optional[datetime] = None
    statut: Optional[str] = None


class DeclCustomsDeclarationUpdate(BaseModel):
    reference: Optional[str] = None
    masse: Optional[str] = None
    regime: Optional[str] = None
    valeur_douane: Optional[float] = None
    date_depot: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclCustomsDeclarationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    masse: Optional[str] = None
    regime: Optional[str] = None
    valeur_douane: Optional[float] = None
    date_depot: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclHsClassificationCreate(BaseModel):
    reference: str
    designation: Optional[str] = None
    code_hs: Optional[str] = None
    taux_droit: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class DeclHsClassificationUpdate(BaseModel):
    reference: Optional[str] = None
    designation: Optional[str] = None
    code_hs: Optional[str] = None
    taux_droit: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclHsClassificationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    designation: Optional[str] = None
    code_hs: Optional[str] = None
    taux_droit: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclOriginCertificateCreate(BaseModel):
    reference: str
    type: Optional[str] = None
    pays_origine: Optional[str] = None
    numero: Optional[str] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None


class DeclOriginCertificateUpdate(BaseModel):
    reference: Optional[str] = None
    type: Optional[str] = None
    pays_origine: Optional[str] = None
    numero: Optional[str] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclOriginCertificateOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type: Optional[str] = None
    pays_origine: Optional[str] = None
    numero: Optional[str] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclCustomsValuationCreate(BaseModel):
    reference: str
    masse: Optional[str] = None
    methode: Optional[str] = None
    valeur: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class DeclCustomsValuationUpdate(BaseModel):
    reference: Optional[str] = None
    masse: Optional[str] = None
    methode: Optional[str] = None
    valeur: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclCustomsValuationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    masse: Optional[str] = None
    methode: Optional[str] = None
    valeur: Optional[float] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclIncotermsRecordCreate(BaseModel):
    reference: str
    code: Optional[str] = None
    lieu: Optional[str] = None
    vendeur: Optional[str] = None
    acheteur: Optional[str] = None
    statut: Optional[str] = None


class DeclIncotermsRecordUpdate(BaseModel):
    reference: Optional[str] = None
    code: Optional[str] = None
    lieu: Optional[str] = None
    vendeur: Optional[str] = None
    acheteur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclIncotermsRecordOut(BaseModel):
    id: int
    company_id: int
    reference: str
    code: Optional[str] = None
    lieu: Optional[str] = None
    vendeur: Optional[str] = None
    acheteur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclImportLicenseCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    quota: Optional[int] = None
    utilisable: Optional[int] = None
    validite: Optional[date] = None
    statut: Optional[str] = None


class DeclImportLicenseUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    quota: Optional[int] = None
    utilisable: Optional[int] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclImportLicenseOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    quota: Optional[int] = None
    utilisable: Optional[int] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclExportLicenseCreate(BaseModel):
    reference: str
    bien: Optional[str] = None
    destination: Optional[str] = None
    usage: Optional[str] = None
    validite: Optional[date] = None
    statut: Optional[str] = None


class DeclExportLicenseUpdate(BaseModel):
    reference: Optional[str] = None
    bien: Optional[str] = None
    destination: Optional[str] = None
    usage: Optional[str] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclExportLicenseOut(BaseModel):
    id: int
    company_id: int
    reference: str
    bien: Optional[str] = None
    destination: Optional[str] = None
    usage: Optional[str] = None
    validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclPreClearanceCreate(BaseModel):
    reference: str
    masse: Optional[str] = None
    arrivee_prevue: Optional[datetime] = None
    depot: Optional[datetime] = None
    statut: Optional[str] = None


class DeclPreClearanceUpdate(BaseModel):
    reference: Optional[str] = None
    masse: Optional[str] = None
    arrivee_prevue: Optional[datetime] = None
    depot: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclPreClearanceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    masse: Optional[str] = None
    arrivee_prevue: Optional[datetime] = None
    depot: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclCustomsInvoiceCreate(BaseModel):
    reference: str
    fournisseur: Optional[str] = None
    montant: Optional[float] = None
    devise: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class DeclCustomsInvoiceUpdate(BaseModel):
    reference: Optional[str] = None
    fournisseur: Optional[str] = None
    montant: Optional[float] = None
    devise: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclCustomsInvoiceOut(BaseModel):
    id: int
    company_id: int
    reference: str
    fournisseur: Optional[str] = None
    montant: Optional[float] = None
    devise: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclPackingListCreate(BaseModel):
    reference: str
    masse: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_net: Optional[float] = None
    statut: Optional[str] = None


class DeclPackingListUpdate(BaseModel):
    reference: Optional[str] = None
    masse: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_net: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclPackingListOut(BaseModel):
    id: int
    company_id: int
    reference: str
    masse: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_net: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclCertificateAnalysisCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    laboratoire: Optional[str] = None
    parametres: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class DeclCertificateAnalysisUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    laboratoire: Optional[str] = None
    parametres: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclCertificateAnalysisOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    laboratoire: Optional[str] = None
    parametres: Optional[str] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclPhytosanitaryAppCreate(BaseModel):
    reference: str
    produit: Optional[str] = None
    destination: Optional[str] = None
    date_controle: Optional[date] = None
    statut: Optional[str] = None


class DeclPhytosanitaryAppUpdate(BaseModel):
    reference: Optional[str] = None
    produit: Optional[str] = None
    destination: Optional[str] = None
    date_controle: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclPhytosanitaryAppOut(BaseModel):
    id: int
    company_id: int
    reference: str
    produit: Optional[str] = None
    destination: Optional[str] = None
    date_controle: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclCustomsPaymentCreate(BaseModel):
    reference: str
    declaration: Optional[str] = None
    montant: Optional[float] = None
    type_droit: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class DeclCustomsPaymentUpdate(BaseModel):
    reference: Optional[str] = None
    declaration: Optional[str] = None
    montant: Optional[float] = None
    type_droit: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclCustomsPaymentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    declaration: Optional[str] = None
    montant: Optional[float] = None
    type_droit: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclTransitDocumentCreate(BaseModel):
    reference: str
    type: Optional[str] = None
    bureau_depart: Optional[str] = None
    bureau_arrivee: Optional[str] = None
    garantie: Optional[float] = None
    statut: Optional[str] = None


class DeclTransitDocumentUpdate(BaseModel):
    reference: Optional[str] = None
    type: Optional[str] = None
    bureau_depart: Optional[str] = None
    bureau_arrivee: Optional[str] = None
    garantie: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclTransitDocumentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type: Optional[str] = None
    bureau_depart: Optional[str] = None
    bureau_arrivee: Optional[str] = None
    garantie: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclDangerousGoodsCreate(BaseModel):
    reference: str
    numero_onu: Optional[str] = None
    classe: Optional[str] = None
    quantite: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class DeclDangerousGoodsUpdate(BaseModel):
    reference: Optional[str] = None
    numero_onu: Optional[str] = None
    classe: Optional[str] = None
    quantite: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclDangerousGoodsOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_onu: Optional[str] = None
    classe: Optional[str] = None
    quantite: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclBondedWarehouseEntryCreate(BaseModel):
    reference: str
    entrepot: Optional[str] = None
    masse: Optional[str] = None
    entree: Optional[datetime] = None
    sortie_prevue: Optional[datetime] = None
    statut: Optional[str] = None


class DeclBondedWarehouseEntryUpdate(BaseModel):
    reference: Optional[str] = None
    entrepot: Optional[str] = None
    masse: Optional[str] = None
    entree: Optional[datetime] = None
    sortie_prevue: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclBondedWarehouseEntryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    entrepot: Optional[str] = None
    masse: Optional[str] = None
    entree: Optional[datetime] = None
    sortie_prevue: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclDutyReliefClaimCreate(BaseModel):
    reference: str
    motif: Optional[str] = None
    declaration: Optional[str] = None
    montant_exonere: Optional[float] = None
    statut: Optional[str] = None


class DeclDutyReliefClaimUpdate(BaseModel):
    reference: Optional[str] = None
    motif: Optional[str] = None
    declaration: Optional[str] = None
    montant_exonere: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclDutyReliefClaimOut(BaseModel):
    id: int
    company_id: int
    reference: str
    motif: Optional[str] = None
    declaration: Optional[str] = None
    montant_exonere: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclManifestCorrectionCreate(BaseModel):
    reference: str
    manifeste: Optional[str] = None
    objet_rectification: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class DeclManifestCorrectionUpdate(BaseModel):
    reference: Optional[str] = None
    manifeste: Optional[str] = None
    objet_rectification: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclManifestCorrectionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    manifeste: Optional[str] = None
    objet_rectification: Optional[str] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DeclCustomsAuditSupportCreate(BaseModel):
    reference: str
    controle: Optional[str] = None
    periode: Optional[str] = None
    pieces_fournies: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None


class DeclCustomsAuditSupportUpdate(BaseModel):
    reference: Optional[str] = None
    controle: Optional[str] = None
    periode: Optional[str] = None
    pieces_fournies: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DeclCustomsAuditSupportOut(BaseModel):
    id: int
    company_id: int
    reference: str
    controle: Optional[str] = None
    periode: Optional[str] = None
    pieces_fournies: Optional[int] = None
    date: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

