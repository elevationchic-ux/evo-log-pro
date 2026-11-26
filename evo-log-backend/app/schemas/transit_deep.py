"""Schemas Pydantic pour transit-douane (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class HsClassificationCreate(BaseModel):
    code_hs: str
    designation: Optional[str] = None
    section: Optional[str] = None
    chapitre: Optional[str] = None
    position: Optional[str] = None
    sous_position: Optional[str] = None
    unite_mesure: Optional[str] = None
    statut: Optional[str] = None


class HsClassificationUpdate(BaseModel):
    code_hs: Optional[str] = None
    designation: Optional[str] = None
    section: Optional[str] = None
    chapitre: Optional[str] = None
    position: Optional[str] = None
    sous_position: Optional[str] = None
    unite_mesure: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class HsClassificationOut(BaseModel):
    id: int
    company_id: int
    code_hs: str
    designation: Optional[str] = None
    section: Optional[str] = None
    chapitre: Optional[str] = None
    position: Optional[str] = None
    sous_position: Optional[str] = None
    unite_mesure: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CustomsValuationCreate(BaseModel):
    reference_dossier: str
    dum_id: Optional[int] = None
    methode_evaluation: Optional[str] = None
    incoterm: Optional[str] = None
    valeur_declaree_xaf: Optional[float] = None
    valeur_transport_xaf: Optional[float] = None
    valeur_assurance_xaf: Optional[float] = None
    valeur_douane_xaf: Optional[float] = None
    taux_change: Optional[float] = None
    date_evaluation: Optional[date] = None
    justification: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class CustomsValuationUpdate(BaseModel):
    reference_dossier: Optional[str] = None
    dum_id: Optional[int] = None
    methode_evaluation: Optional[str] = None
    incoterm: Optional[str] = None
    valeur_declaree_xaf: Optional[float] = None
    valeur_transport_xaf: Optional[float] = None
    valeur_assurance_xaf: Optional[float] = None
    valeur_douane_xaf: Optional[float] = None
    taux_change: Optional[float] = None
    date_evaluation: Optional[date] = None
    justification: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomsValuationOut(BaseModel):
    id: int
    company_id: int
    reference_dossier: str
    dum_id: Optional[int] = None
    methode_evaluation: Optional[str] = None
    incoterm: Optional[str] = None
    valeur_declaree_xaf: Optional[float] = None
    valeur_transport_xaf: Optional[float] = None
    valeur_assurance_xaf: Optional[float] = None
    valeur_douane_xaf: Optional[float] = None
    taux_change: Optional[float] = None
    date_evaluation: Optional[date] = None
    justification: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class OriginCertificateCreate(BaseModel):
    numero_certificat: str
    type_certificat: Optional[str] = None
    pays_origine: Optional[str] = None
    exportateur: Optional[str] = None
    importateur: Optional[str] = None
    dum_id: Optional[int] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    chambre_delivrance: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class OriginCertificateUpdate(BaseModel):
    numero_certificat: Optional[str] = None
    type_certificat: Optional[str] = None
    pays_origine: Optional[str] = None
    exportateur: Optional[str] = None
    importateur: Optional[str] = None
    dum_id: Optional[int] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    chambre_delivrance: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class OriginCertificateOut(BaseModel):
    id: int
    company_id: int
    numero_certificat: str
    type_certificat: Optional[str] = None
    pays_origine: Optional[str] = None
    exportateur: Optional[str] = None
    importateur: Optional[str] = None
    dum_id: Optional[int] = None
    date_emission: Optional[date] = None
    date_expiration: Optional[date] = None
    chambre_delivrance: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BondedWarehouseCreate(BaseModel):
    code_entrepot: str
    nom: Optional[str] = None
    agrement_numero: Optional[str] = None
    date_debut_agrement: Optional[date] = None
    date_fin_agrement: Optional[date] = None
    capacite_m2: Optional[float] = None
    localisation: Optional[str] = None
    gestionnaire: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class BondedWarehouseUpdate(BaseModel):
    code_entrepot: Optional[str] = None
    nom: Optional[str] = None
    agrement_numero: Optional[str] = None
    date_debut_agrement: Optional[date] = None
    date_fin_agrement: Optional[date] = None
    capacite_m2: Optional[float] = None
    localisation: Optional[str] = None
    gestionnaire: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class BondedWarehouseOut(BaseModel):
    id: int
    company_id: int
    code_entrepot: str
    nom: Optional[str] = None
    agrement_numero: Optional[str] = None
    date_debut_agrement: Optional[date] = None
    date_fin_agrement: Optional[date] = None
    capacite_m2: Optional[float] = None
    localisation: Optional[str] = None
    gestionnaire: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TransitGuaranteeCreate(BaseModel):
    reference_caution: str
    type_garantie: Optional[str] = None
    banque_emettrice: Optional[str] = None
    donneur_ordre: Optional[str] = None
    montant_caution_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class TransitGuaranteeUpdate(BaseModel):
    reference_caution: Optional[str] = None
    type_garantie: Optional[str] = None
    banque_emettrice: Optional[str] = None
    donneur_ordre: Optional[str] = None
    montant_caution_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class TransitGuaranteeOut(BaseModel):
    id: int
    company_id: int
    reference_caution: str
    type_garantie: Optional[str] = None
    banque_emettrice: Optional[str] = None
    donneur_ordre: Optional[str] = None
    montant_caution_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ExportDeclarationCreate(BaseModel):
    numero_dge: str
    declarant: Optional[str] = None
    exportateur: Optional[str] = None
    pays_destination: Optional[str] = None
    valeur_xaf: Optional[float] = None
    poids_net_kg: Optional[float] = None
    regime: Optional[str] = None
    date_depot: Optional[date] = None
    date_validation: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class ExportDeclarationUpdate(BaseModel):
    numero_dge: Optional[str] = None
    declarant: Optional[str] = None
    exportateur: Optional[str] = None
    pays_destination: Optional[str] = None
    valeur_xaf: Optional[float] = None
    poids_net_kg: Optional[float] = None
    regime: Optional[str] = None
    date_depot: Optional[date] = None
    date_validation: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ExportDeclarationOut(BaseModel):
    id: int
    company_id: int
    numero_dge: str
    declarant: Optional[str] = None
    exportateur: Optional[str] = None
    pays_destination: Optional[str] = None
    valeur_xaf: Optional[float] = None
    poids_net_kg: Optional[float] = None
    regime: Optional[str] = None
    date_depot: Optional[date] = None
    date_validation: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProhibitedGoodCreate(BaseModel):
    code_produit: str
    designation: Optional[str] = None
    code_hs: Optional[str] = None
    categorie: Optional[str] = None
    base_legale: Optional[str] = None
    autorite_competente: Optional[str] = None
    conditions_regime: Optional[str] = None
    actif: Optional[bool] = None


class ProhibitedGoodUpdate(BaseModel):
    code_produit: Optional[str] = None
    designation: Optional[str] = None
    code_hs: Optional[str] = None
    categorie: Optional[str] = None
    base_legale: Optional[str] = None
    autorite_competente: Optional[str] = None
    conditions_regime: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class ProhibitedGoodOut(BaseModel):
    id: int
    company_id: int
    code_produit: str
    designation: Optional[str] = None
    code_hs: Optional[str] = None
    categorie: Optional[str] = None
    base_legale: Optional[str] = None
    autorite_competente: Optional[str] = None
    conditions_regime: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CustomsRegimeCreate(BaseModel):
    reference_regime: str
    dum_id: Optional[int] = None
    type_regime: Optional[str] = None
    duree_max_mois: Optional[int] = None
    date_appllication: Optional[date] = None
    date_echeance: Optional[date] = None
    caution_associee: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class CustomsRegimeUpdate(BaseModel):
    reference_regime: Optional[str] = None
    dum_id: Optional[int] = None
    type_regime: Optional[str] = None
    duree_max_mois: Optional[int] = None
    date_appllication: Optional[date] = None
    date_echeance: Optional[date] = None
    caution_associee: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomsRegimeOut(BaseModel):
    id: int
    company_id: int
    reference_regime: str
    dum_id: Optional[int] = None
    type_regime: Optional[str] = None
    duree_max_mois: Optional[int] = None
    date_appllication: Optional[date] = None
    date_echeance: Optional[date] = None
    caution_associee: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PhysicalInspectionCreate(BaseModel):
    numero_pv: str
    dum_id: Optional[int] = None
    canal: Optional[str] = None
    inspecteur: Optional[str] = None
    date_inspection: Optional[datetime] = None
    lieu: Optional[str] = None
    resultat: Optional[str] = None
    ecart_poids_kg: Optional[float] = None
    ecart_colis: Optional[int] = None
    observations: Optional[str] = None
    statut: Optional[str] = None


class PhysicalInspectionUpdate(BaseModel):
    numero_pv: Optional[str] = None
    dum_id: Optional[int] = None
    canal: Optional[str] = None
    inspecteur: Optional[str] = None
    date_inspection: Optional[datetime] = None
    lieu: Optional[str] = None
    resultat: Optional[str] = None
    ecart_poids_kg: Optional[float] = None
    ecart_colis: Optional[int] = None
    observations: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PhysicalInspectionOut(BaseModel):
    id: int
    company_id: int
    numero_pv: str
    dum_id: Optional[int] = None
    canal: Optional[str] = None
    inspecteur: Optional[str] = None
    date_inspection: Optional[datetime] = None
    lieu: Optional[str] = None
    resultat: Optional[str] = None
    ecart_poids_kg: Optional[float] = None
    ecart_colis: Optional[int] = None
    observations: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DutyPaymentCreate(BaseModel):
    numero_quittance: str
    dum_id: Optional[int] = None
    type_paiement: Optional[str] = None
    droits_percus_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    taxe_statistique_xaf: Optional[float] = None
    redevance_id: Optional[str] = None
    mode_reglement: Optional[str] = None
    date_paiement: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class DutyPaymentUpdate(BaseModel):
    numero_quittance: Optional[str] = None
    dum_id: Optional[int] = None
    type_paiement: Optional[str] = None
    droits_percus_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    taxe_statistique_xaf: Optional[float] = None
    redevance_id: Optional[str] = None
    mode_reglement: Optional[str] = None
    date_paiement: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class DutyPaymentOut(BaseModel):
    id: int
    company_id: int
    numero_quittance: str
    dum_id: Optional[int] = None
    type_paiement: Optional[str] = None
    droits_percus_xaf: Optional[float] = None
    tva_xaf: Optional[float] = None
    taxe_statistique_xaf: Optional[float] = None
    redevance_id: Optional[str] = None
    mode_reglement: Optional[str] = None
    date_paiement: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TraderRegistrationCreate(BaseModel):
    numero_operateur: str
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    rc_number: Optional[str] = None
    type_operateur: Optional[str] = None
    statut_oea: Optional[str] = None
    date_agrement: Optional[date] = None
    date_expiration: Optional[date] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    notes: Optional[str] = None


class TraderRegistrationUpdate(BaseModel):
    numero_operateur: Optional[str] = None
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    rc_number: Optional[str] = None
    type_operateur: Optional[str] = None
    statut_oea: Optional[str] = None
    date_agrement: Optional[date] = None
    date_expiration: Optional[date] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class TraderRegistrationOut(BaseModel):
    id: int
    company_id: int
    numero_operateur: str
    raison_sociale: Optional[str] = None
    niu: Optional[str] = None
    rc_number: Optional[str] = None
    type_operateur: Optional[str] = None
    statut_oea: Optional[str] = None
    date_agrement: Optional[date] = None
    date_expiration: Optional[date] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TariffReferenceCreate(BaseModel):
    code_ligne_tarifaire: str
    code_hs: Optional[str] = None
    designation: Optional[str] = None
    droit_base_pct: Optional[float] = None
    cotisation_compensatoire_pct: Optional[float] = None
    taxe_foretiaire_pct: Optional[float] = None
    redevance_statistique_pct: Optional[float] = None
    tva_pct: Optional[float] = None
    categorie_produit: Optional[str] = None
    date_application: Optional[date] = None
    date_fin: Optional[date] = None


class TariffReferenceUpdate(BaseModel):
    code_ligne_tarifaire: Optional[str] = None
    code_hs: Optional[str] = None
    designation: Optional[str] = None
    droit_base_pct: Optional[float] = None
    cotisation_compensatoire_pct: Optional[float] = None
    taxe_foretiaire_pct: Optional[float] = None
    redevance_statistique_pct: Optional[float] = None
    tva_pct: Optional[float] = None
    categorie_produit: Optional[str] = None
    date_application: Optional[date] = None
    date_fin: Optional[date] = None
    is_active: Optional[bool] = None


class TariffReferenceOut(BaseModel):
    id: int
    company_id: int
    code_ligne_tarifaire: str
    code_hs: Optional[str] = None
    designation: Optional[str] = None
    droit_base_pct: Optional[float] = None
    cotisation_compensatoire_pct: Optional[float] = None
    taxe_foretiaire_pct: Optional[float] = None
    redevance_statistique_pct: Optional[float] = None
    tva_pct: Optional[float] = None
    categorie_produit: Optional[str] = None
    date_application: Optional[date] = None
    date_fin: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

