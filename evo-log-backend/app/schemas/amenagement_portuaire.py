"""Contrats Pydantic du departement Amenagement portuaire.

Regle d'honnete : tout champ mesurable ou juridique est Optionnel et n'a AUCUN
defaut calcule. Une creation sans date d'approbation laisse NULL (affiche
« non enregistre »), jamais une date par defaut type « today ». Les enums
repris du modele SQLAlchemy garantissent que seule la nomenclature reelle du
circuit camerounais est acceptee.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

from app.models.amenagement_portuaire import (
    TypeSchema, StatutSchema,
    TypeProjet, StatutProjet, OrigineFinancement,
    TypeMarche, CodeMarche, StatutMarche,
    TypeTitreDomanial,
    TypeContratExploitation, StatutContrat,
    TypeInfrastructure, EtatInfrastructure,
    TypeDragage,
    TypeAutorisationTravaux, StatutAutorisation,
)


class _Conf(BaseModel):
    """Base commune : lecture directe depuis les objets ORM."""
    model_config = {"from_attributes": True}


class _Provenance(BaseModel):
    """Champs communs de tracabilite de la saisie (aucune donnee devinee)."""
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None


# ─── 1. Schémas directeurs ───────────────────────────────────────────────────

class SchemaDirecteurCreate(_Provenance):
    code: str = Field(min_length=2, max_length=40)
    libelle: str = Field(min_length=3, max_length=200)
    port_id: Optional[int] = None
    type_schema: TypeSchema = TypeSchema.SCHEMA_DIRECTEUR
    perimetre: Optional[str] = None
    horizon_debut: Optional[int] = None
    horizon_fin: Optional[int] = None
    statut: StatutSchema = StatutSchema.ELABORATION
    autorite_elaboratrice: Optional[str] = None
    reference_approbatrice: Optional[str] = None
    date_approbation: Optional[date] = None
    date_depot: Optional[date] = None
    date_echeance_revision: Optional[date] = None
    cout_elaboration_xaf: Optional[float] = None
    budget_alloue_travaux_xaf: Optional[float] = None
    superficie_totale_ha: Optional[float] = None
    surface_eau_ha: Optional[float] = None
    lignes_directrices: Optional[List[str]] = None
    documents_sources: Optional[List[str]] = None


class SchemaDirecteurUpdate(BaseModel):
    libelle: Optional[str] = None
    port_id: Optional[int] = None
    type_schema: Optional[TypeSchema] = None
    perimetre: Optional[str] = None
    horizon_debut: Optional[int] = None
    horizon_fin: Optional[int] = None
    statut: Optional[StatutSchema] = None
    autorite_elaboratrice: Optional[str] = None
    reference_approbatrice: Optional[str] = None
    date_approbation: Optional[date] = None
    date_depot: Optional[date] = None
    date_echeance_revision: Optional[date] = None
    cout_elaboration_xaf: Optional[float] = None
    budget_alloue_travaux_xaf: Optional[float] = None
    superficie_totale_ha: Optional[float] = None
    surface_eau_ha: Optional[float] = None
    lignes_directrices: Optional[List[str]] = None
    documents_sources: Optional[List[str]] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None
    est_actif: Optional[bool] = None


class SchemaDirecteurOut(_Conf):
    id: int
    code: str
    libelle: str
    port_id: Optional[int] = None
    type_schema: Optional[TypeSchema] = None
    perimetre: Optional[str] = None
    horizon_debut: Optional[int] = None
    horizon_fin: Optional[int] = None
    statut: Optional[StatutSchema] = None
    autorite_elaboratrice: Optional[str] = None
    reference_approbatrice: Optional[str] = None
    date_approbation: Optional[date] = None
    date_depot: Optional[date] = None
    date_echeance_revision: Optional[date] = None
    cout_elaboration_xaf: Optional[float] = None
    budget_alloue_travaux_xaf: Optional[float] = None
    superficie_totale_ha: Optional[float] = None
    surface_eau_ha: Optional[float] = None
    lignes_directrices: Optional[Any] = None
    documents_sources: Optional[Any] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    est_actif: bool
    created_at: Optional[datetime] = None


# ─── 2. Projets d'aménagement ────────────────────────────────────────────────

class ProjetAmenagementCreate(_Provenance):
    code_projet: str = Field(min_length=2, max_length=40)
    libelle: str = Field(min_length=3, max_length=200)
    description: Optional[str] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    schema_id: Optional[int] = None
    type_ouvrage: TypeProjet = TypeProjet.AUTRE
    statut: StatutProjet = StatutProjet.IDENTIFIE
    priorite: Optional[str] = None
    origines_financement: Optional[List[str]] = None
    cout_previsionnel_xaf: Optional[float] = None
    cout_reel_xaf: Optional[float] = None
    devise: Optional[str] = "XAF"
    financement_public_xaf: Optional[float] = None
    financement_prive_xaf: Optional[float] = None
    date_debut_prevue: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_reelle_demarrage: Optional[date] = None
    date_reelle_achevement: Optional[date] = None
    avancement_physique_pct: Optional[float] = None
    avancement_financier_pct: Optional[float] = None
    maitre_ouvrage: Optional[str] = None
    maitre_doeuvre: Optional[str] = None
    bureau_controle: Optional[str] = None
    entreprise_attributaire: Optional[str] = None
    reference_fiche_technique: Optional[str] = None
    date_notification_minfi: Optional[date] = None
    eies_obligatoire: Optional[bool] = None
    superficie_impactee_ha: Optional[float] = None
    capacite_additionnelle: Optional[str] = None
    justificatif_utilite: Optional[str] = None
    risques: Optional[List[str]] = None


class ProjetAmenagementUpdate(BaseModel):
    libelle: Optional[str] = None
    description: Optional[str] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    schema_id: Optional[int] = None
    type_ouvrage: Optional[TypeProjet] = None
    statut: Optional[StatutProjet] = None
    priorite: Optional[str] = None
    origines_financement: Optional[List[str]] = None
    cout_previsionnel_xaf: Optional[float] = None
    cout_reel_xaf: Optional[float] = None
    devise: Optional[str] = None
    financement_public_xaf: Optional[float] = None
    financement_prive_xaf: Optional[float] = None
    date_debut_prevue: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_reelle_demarrage: Optional[date] = None
    date_reelle_achevement: Optional[date] = None
    avancement_physique_pct: Optional[float] = None
    avancement_financier_pct: Optional[float] = None
    maitre_ouvrage: Optional[str] = None
    maitre_doeuvre: Optional[str] = None
    bureau_controle: Optional[str] = None
    entreprise_attributaire: Optional[str] = None
    reference_fiche_technique: Optional[str] = None
    date_notification_minfi: Optional[date] = None
    eies_obligatoire: Optional[bool] = None
    superficie_impactee_ha: Optional[float] = None
    capacite_additionnelle: Optional[str] = None
    justificatif_utilite: Optional[str] = None
    risques: Optional[List[str]] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None
    est_actif: Optional[bool] = None


class ProjetAmenagementOut(_Conf):
    id: int
    code_projet: str
    libelle: str
    description: Optional[str] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    schema_id: Optional[int] = None
    type_ouvrage: Optional[TypeProjet] = None
    statut: Optional[StatutProjet] = None
    priorite: Optional[str] = None
    origines_financement: Optional[Any] = None
    cout_previsionnel_xaf: Optional[float] = None
    cout_reel_xaf: Optional[float] = None
    devise: Optional[str] = None
    financement_public_xaf: Optional[float] = None
    financement_prive_xaf: Optional[float] = None
    date_debut_prevue: Optional[date] = None
    date_fin_prevue: Optional[date] = None
    date_reelle_demarrage: Optional[date] = None
    date_reelle_achevement: Optional[date] = None
    avancement_physique_pct: Optional[float] = None
    avancement_financier_pct: Optional[float] = None
    maitre_ouvrage: Optional[str] = None
    maitre_doeuvre: Optional[str] = None
    bureau_controle: Optional[str] = None
    entreprise_attributaire: Optional[str] = None
    reference_fiche_technique: Optional[str] = None
    date_notification_minfi: Optional[date] = None
    eies_obligatoire: Optional[bool] = None
    superficie_impactee_ha: Optional[float] = None
    capacite_additionnelle: Optional[str] = None
    justificatif_utilite: Optional[str] = None
    risques: Optional[Any] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    est_actif: bool
    created_at: Optional[datetime] = None


# ─── 3. Programmation : fiche technique, maturité, engagement ────────────────

class DocumentProgrammationCreate(_Provenance):
    reference_fiche_technique: str = Field(
        min_length=2, max_length=80,
        description="Reference reellement attribuee a la fiche / au dossier technique",
    )
    exercice: int
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    objet: str = Field(min_length=3, max_length=300)
    montant_inscrit_xaf: Optional[float] = None
    montant_paye_xaf: Optional[float] = None
    source_financement: Optional[OrigineFinancement] = None
    chapitre: Optional[str] = None
    statut: Optional[str] = None
    date_presentation: Optional[date] = None
    numero_visa_maturite: Optional[str] = None
    date_visa_maturite: Optional[date] = None
    autorite_visa_maturite: Optional[str] = None
    reference_pip_cdmt: Optional[str] = None
    date_visa_controle_financier: Optional[date] = None
    autorite_visa: Optional[str] = None
    numero_engagement: Optional[str] = None
    date_notification_minfi: Optional[date] = None


class DocumentProgrammationUpdate(BaseModel):
    exercice: Optional[int] = None
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    objet: Optional[str] = None
    montant_inscrit_xaf: Optional[float] = None
    montant_paye_xaf: Optional[float] = None
    source_financement: Optional[OrigineFinancement] = None
    chapitre: Optional[str] = None
    statut: Optional[str] = None
    date_presentation: Optional[date] = None
    numero_visa_maturite: Optional[str] = None
    date_visa_maturite: Optional[date] = None
    autorite_visa_maturite: Optional[str] = None
    reference_pip_cdmt: Optional[str] = None
    date_visa_controle_financier: Optional[date] = None
    autorite_visa: Optional[str] = None
    numero_engagement: Optional[str] = None
    date_notification_minfi: Optional[date] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None


class DocumentProgrammationOut(_Conf):
    id: int
    reference_fiche_technique: str
    exercice: int
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    objet: Optional[str] = None
    montant_inscrit_xaf: Optional[float] = None
    montant_paye_xaf: Optional[float] = None
    source_financement: Optional[OrigineFinancement] = None
    chapitre: Optional[str] = None
    statut: Optional[str] = None
    date_presentation: Optional[date] = None
    numero_visa_maturite: Optional[str] = None
    date_visa_maturite: Optional[date] = None
    autorite_visa_maturite: Optional[str] = None
    reference_pip_cdmt: Optional[str] = None
    date_visa_controle_financier: Optional[date] = None
    autorite_visa: Optional[str] = None
    numero_engagement: Optional[str] = None
    date_notification_minfi: Optional[date] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ─── 4. Marchés & contrats de PPP ────────────────────────────────────────────

class MarcheAmenagementCreate(_Provenance):
    reference: str = Field(min_length=2, max_length=80)
    designations: str = Field(min_length=3, max_length=300)
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    type_marche: TypeMarche = TypeMarche.TRAVAUX
    code_marche: Optional[CodeMarche] = None
    statut: StatutMarche = StatutMarche.PREVU
    procedure_controle: Optional[str] = None
    dossier_appel_offre: Optional[str] = None
    date_publication_dao: Optional[date] = None
    date_remise_offres: Optional[date] = None
    date_colife: Optional[date] = None
    avis_colife: Optional[str] = None
    date_attribution: Optional[date] = None
    attributaire: Optional[str] = None
    montant_attribue_xaf: Optional[float] = None
    montant_initial_xaf: Optional[float] = None
    montant_final_xaf: Optional[float] = None
    devise: Optional[str] = "XAF"
    part_pmp_pct: Optional[float] = None
    avance_demarrage_xaf: Optional[float] = None
    retenue_garantie_pct: Optional[float] = None
    caution_banque: Optional[str] = None
    delai_execution_mois: Optional[int] = None
    date_notification: Optional[date] = None
    date_ouverture_chantier: Optional[date] = None
    date_reception_provisoire: Optional[date] = None
    date_reception_definitive: Optional[date] = None
    garant_result_annees: Optional[int] = None
    nrd_max_jours: Optional[int] = None


class MarcheAmenagementUpdate(BaseModel):
    designations: Optional[str] = None
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    type_marche: Optional[TypeMarche] = None
    code_marche: Optional[CodeMarche] = None
    statut: Optional[StatutMarche] = None
    procedure_controle: Optional[str] = None
    dossier_appel_offre: Optional[str] = None
    date_publication_dao: Optional[date] = None
    date_remise_offres: Optional[date] = None
    date_colife: Optional[date] = None
    avis_colife: Optional[str] = None
    date_attribution: Optional[date] = None
    attributaire: Optional[str] = None
    montant_attribue_xaf: Optional[float] = None
    montant_initial_xaf: Optional[float] = None
    montant_final_xaf: Optional[float] = None
    devise: Optional[str] = None
    part_pmp_pct: Optional[float] = None
    avance_demarrage_xaf: Optional[float] = None
    retenue_garantie_pct: Optional[float] = None
    caution_banque: Optional[str] = None
    delai_execution_mois: Optional[int] = None
    date_notification: Optional[date] = None
    date_ouverture_chantier: Optional[date] = None
    date_reception_provisoire: Optional[date] = None
    date_reception_definitive: Optional[date] = None
    garant_result_annees: Optional[int] = None
    nrd_max_jours: Optional[int] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None


class MarcheAmenagementOut(_Conf):
    id: int
    reference: str
    designations: str
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    type_marche: Optional[TypeMarche] = None
    code_marche: Optional[CodeMarche] = None
    statut: Optional[StatutMarche] = None
    procedure_controle: Optional[str] = None
    dossier_appel_offre: Optional[str] = None
    date_publication_dao: Optional[date] = None
    date_remise_offres: Optional[date] = None
    date_colife: Optional[date] = None
    avis_colife: Optional[str] = None
    date_attribution: Optional[date] = None
    attributaire: Optional[str] = None
    montant_attribue_xaf: Optional[float] = None
    montant_initial_xaf: Optional[float] = None
    montant_final_xaf: Optional[float] = None
    devise: Optional[str] = None
    part_pmp_pct: Optional[float] = None
    avance_demarrage_xaf: Optional[float] = None
    retenue_garantie_pct: Optional[float] = None
    caution_banque: Optional[str] = None
    delai_execution_mois: Optional[int] = None
    date_notification: Optional[date] = None
    date_ouverture_chantier: Optional[date] = None
    date_reception_provisoire: Optional[date] = None
    date_reception_definitive: Optional[date] = None
    garant_result_annees: Optional[int] = None
    nrd_max_jours: Optional[int] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ─── 5. Titres domaniaux ─────────────────────────────────────────────────────

class AutorisationDomanialeCreate(_Provenance):
    numero_piece: str = Field(min_length=2, max_length=80)
    type_titre: TypeTitreDomanial
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    zone_id: Optional[int] = None
    beneficiaire: str = Field(min_length=2, max_length=200)
    objet: Optional[str] = None
    assiette: Optional[str] = None
    superficie_m2: Optional[float] = None
    destination: Optional[str] = None
    redevance_annuelle_xaf: Optional[float] = None
    taux_redevance: Optional[str] = None
    date_demande: Optional[date] = None
    date_signature: Optional[date] = None
    date_effet: Optional[date] = None
    date_expiration: Optional[date] = None
    renouvelable: Optional[bool] = None
    delai_renouvellement_mois: Optional[int] = None
    autorite_emettrice: Optional[str] = None
    reference_deliberation: Optional[str] = None
    piece_jointe: Optional[str] = None
    statut: Optional[str] = None
    motif_refus: Optional[str] = None


class AutorisationDomanialeUpdate(BaseModel):
    type_titre: Optional[TypeTitreDomanial] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    zone_id: Optional[int] = None
    beneficiaire: Optional[str] = None
    objet: Optional[str] = None
    assiette: Optional[str] = None
    superficie_m2: Optional[float] = None
    destination: Optional[str] = None
    redevance_annuelle_xaf: Optional[float] = None
    taux_redevance: Optional[str] = None
    date_demande: Optional[date] = None
    date_signature: Optional[date] = None
    date_effet: Optional[date] = None
    date_expiration: Optional[date] = None
    renouvelable: Optional[bool] = None
    delai_renouvellement_mois: Optional[int] = None
    autorite_emettrice: Optional[str] = None
    reference_deliberation: Optional[str] = None
    piece_jointe: Optional[str] = None
    statut: Optional[str] = None
    motif_refus: Optional[str] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None


class AutorisationDomanialeOut(_Conf):
    id: int
    numero_piece: str
    type_titre: Optional[TypeTitreDomanial] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    zone_id: Optional[int] = None
    beneficiaire: Optional[str] = None
    objet: Optional[str] = None
    assiette: Optional[str] = None
    superficie_m2: Optional[float] = None
    destination: Optional[str] = None
    redevance_annuelle_xaf: Optional[float] = None
    taux_redevance: Optional[str] = None
    date_demande: Optional[date] = None
    date_signature: Optional[date] = None
    date_effet: Optional[date] = None
    date_expiration: Optional[date] = None
    renouvelable: Optional[bool] = None
    delai_renouvellement_mois: Optional[int] = None
    autorite_emettrice: Optional[str] = None
    reference_deliberation: Optional[str] = None
    piece_jointe: Optional[str] = None
    statut: Optional[str] = None
    motif_refus: Optional[str] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ─── 6. Concessions & contrats d'exploitation ────────────────────────────────

class ConcessionPortuaireCreate(_Provenance):
    code_contrat: str = Field(min_length=2, max_length=60)
    nom_contrat: str = Field(min_length=3, max_length=200)
    port_id: int
    terminal_id: Optional[int] = None
    type_contrat: TypeContratExploitation
    statut: StatutContrat = StatutContrat.NEGOCIATION
    autorite_concedante: str = Field(min_length=2, max_length=160)
    concessionnaire: str = Field(min_length=2, max_length=200)
    groupe_final: Optional[str] = None
    objet: Optional[str] = None
    perimetre: Optional[str] = None
    superficie_concedee_ha: Optional[float] = None
    longueur_quai_ml: Optional[float] = None
    capacite_contractuelle: Optional[str] = None
    date_effet: Optional[date] = None
    date_echeance: Optional[date] = None
    duree_mois: Optional[int] = None
    prolongations: Optional[List[Dict[str, Any]]] = None
    investissement_promis_xaf: Optional[float] = None
    investissement_realise_xaf: Optional[float] = None
    redevance_concession_xaf: Optional[float] = None
    redevance_par_unite: Optional[float] = None
    unite_redevance: Optional[str] = None
    clauses_revolution: Optional[str] = None
    sanctions_contractuelles: Optional[str] = None
    biens_reversibles: Optional[str] = None
    reference_approbation: Optional[str] = None
    date_approbation: Optional[date] = None
    arret_travail: Optional[bool] = None


class ConcessionPortuaireUpdate(BaseModel):
    nom_contrat: Optional[str] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    type_contrat: Optional[TypeContratExploitation] = None
    statut: Optional[StatutContrat] = None
    autorite_concedante: Optional[str] = None
    concessionnaire: Optional[str] = None
    groupe_final: Optional[str] = None
    objet: Optional[str] = None
    perimetre: Optional[str] = None
    superficie_concedee_ha: Optional[float] = None
    longueur_quai_ml: Optional[float] = None
    capacite_contractuelle: Optional[str] = None
    date_effet: Optional[date] = None
    date_echeance: Optional[date] = None
    duree_mois: Optional[int] = None
    prolongations: Optional[List[Dict[str, Any]]] = None
    investissement_promis_xaf: Optional[float] = None
    investissement_realise_xaf: Optional[float] = None
    redevance_concession_xaf: Optional[float] = None
    redevance_par_unite: Optional[float] = None
    unite_redevance: Optional[str] = None
    clauses_revolution: Optional[str] = None
    sanctions_contractuelles: Optional[str] = None
    biens_reversibles: Optional[str] = None
    reference_approbation: Optional[str] = None
    date_approbation: Optional[date] = None
    arret_travail: Optional[bool] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None


class ConcessionPortuaireOut(_Conf):
    id: int
    code_contrat: str
    nom_contrat: str
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    type_contrat: Optional[TypeContratExploitation] = None
    statut: Optional[StatutContrat] = None
    autorite_concedante: Optional[str] = None
    concessionnaire: Optional[str] = None
    groupe_final: Optional[str] = None
    objet: Optional[str] = None
    perimetre: Optional[str] = None
    superficie_concedee_ha: Optional[float] = None
    longueur_quai_ml: Optional[float] = None
    capacite_contractuelle: Optional[str] = None
    date_effet: Optional[date] = None
    date_echeance: Optional[date] = None
    duree_mois: Optional[int] = None
    prolongations: Optional[Any] = None
    investissement_promis_xaf: Optional[float] = None
    investissement_realise_xaf: Optional[float] = None
    redevance_concession_xaf: Optional[float] = None
    redevance_par_unite: Optional[float] = None
    unite_redevance: Optional[str] = None
    clauses_revolution: Optional[str] = None
    sanctions_contractuelles: Optional[str] = None
    biens_reversibles: Optional[str] = None
    reference_approbation: Optional[str] = None
    date_approbation: Optional[date] = None
    arret_travail: Optional[bool] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ─── 7. Inventaire des infrastructures ───────────────────────────────────────

class InfrastructurePortuaireCreate(_Provenance):
    code: str = Field(min_length=2, max_length=60)
    designation: str = Field(min_length=3, max_length=200)
    type_infrastructure: TypeInfrastructure
    port_id: int
    terminal_id: Optional[int] = None
    projet_id: Optional[int] = None
    zone_id: Optional[int] = None
    emplacement: Optional[str] = None
    statut: EtatInfrastructure = EtatInfrastructure.PROJETEE
    longueur_ml: Optional[float] = None
    largeur_m: Optional[float] = None
    superficie_m2: Optional[float] = None
    profondeur_utile_m: Optional[float] = None
    hauteur_parement_m: Optional[int] = None
    portance_tonnes_m2: Optional[float] = None
    capacite_teus: Optional[int] = None
    date_mise_service: Optional[date] = None
    date_derniere_inspection: Optional[date] = None
    periodicite_inspection_mois: Optional[int] = None
    prochaine_inspection: Optional[date] = None
    etat_structural: Optional[str] = None
    note_genie_civil: Optional[float] = None
    travaux_renovation_prevus: Optional[bool] = None
    estimation_renovation_xaf: Optional[float] = None
    valeur_patrimoniale_xaf: Optional[float] = None
    date_entree_patrimoine: Optional[date] = None
    regime_fiscal: Optional[str] = None
    reversable: Optional[bool] = None
    operateur_entretien: Optional[str] = None
    sources_documents: Optional[List[str]] = None


class InfrastructurePortuaireUpdate(BaseModel):
    designation: Optional[str] = None
    type_infrastructure: Optional[TypeInfrastructure] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    projet_id: Optional[int] = None
    zone_id: Optional[int] = None
    emplacement: Optional[str] = None
    statut: Optional[EtatInfrastructure] = None
    longueur_ml: Optional[float] = None
    largeur_m: Optional[float] = None
    superficie_m2: Optional[float] = None
    profondeur_utile_m: Optional[float] = None
    hauteur_parement_m: Optional[int] = None
    portance_tonnes_m2: Optional[float] = None
    capacite_teus: Optional[int] = None
    date_mise_service: Optional[date] = None
    date_derniere_inspection: Optional[date] = None
    periodicite_inspection_mois: Optional[int] = None
    prochaine_inspection: Optional[date] = None
    etat_structural: Optional[str] = None
    note_genie_civil: Optional[float] = None
    travaux_renovation_prevus: Optional[bool] = None
    estimation_renovation_xaf: Optional[float] = None
    valeur_patrimoniale_xaf: Optional[float] = None
    date_entree_patrimoine: Optional[date] = None
    regime_fiscal: Optional[str] = None
    reversable: Optional[bool] = None
    operateur_entretien: Optional[str] = None
    sources_documents: Optional[List[str]] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None
    est_actif: Optional[bool] = None


class InfrastructurePortuaireOut(_Conf):
    id: int
    code: str
    designation: str
    type_infrastructure: Optional[TypeInfrastructure] = None
    port_id: Optional[int] = None
    terminal_id: Optional[int] = None
    projet_id: Optional[int] = None
    zone_id: Optional[int] = None
    emplacement: Optional[str] = None
    statut: Optional[EtatInfrastructure] = None
    longueur_ml: Optional[float] = None
    largeur_m: Optional[float] = None
    superficie_m2: Optional[float] = None
    profondeur_utile_m: Optional[float] = None
    hauteur_parement_m: Optional[int] = None
    portance_tonnes_m2: Optional[float] = None
    capacite_teus: Optional[int] = None
    date_mise_service: Optional[date] = None
    date_derniere_inspection: Optional[date] = None
    periodicite_inspection_mois: Optional[int] = None
    prochaine_inspection: Optional[date] = None
    etat_structural: Optional[str] = None
    note_genie_civil: Optional[float] = None
    travaux_renovation_prevus: Optional[bool] = None
    estimation_renovation_xaf: Optional[float] = None
    valeur_patrimoniale_xaf: Optional[float] = None
    date_entree_patrimoine: Optional[date] = None
    regime_fiscal: Optional[str] = None
    reversable: Optional[bool] = None
    operateur_entretien: Optional[str] = None
    sources_documents: Optional[Any] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    est_actif: bool
    created_at: Optional[datetime] = None


# ─── 8. Campagnes de dragage ─────────────────────────────────────────────────

class DragageCreate(_Provenance):
    code_campagne: str = Field(min_length=2, max_length=60)
    libelle: str = Field(min_length=3, max_length=200)
    port_id: int
    projet_id: Optional[int] = None
    type_dragage: TypeDragage = TypeDragage.ENTRETIEN
    zone_traitee: Optional[str] = None
    superficie_draguee_m2: Optional[float] = None
    volume_mesure_m3: Optional[float] = None
    volume_facture_m3: Optional[float] = None
    profondeur_avant_m: Optional[float] = None
    profondeur_visee_m: Optional[float] = None
    profondeur_obtenue_m: Optional[float] = None
    nature_sediment: Optional[str] = None
    exutoire_rejet: Optional[str] = None
    autorisation_rejet_reference: Optional[str] = None
    entreprise: Optional[str] = None
    type_drague: Optional[str] = None
    cout_xaf: Optional[float] = None
    devise: Optional[str] = "XAF"
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    jours_arret: Optional[int] = None
    statut: Optional[str] = None
    leve_bathymetrique_apres: Optional[bool] = None
    date_releve: Optional[date] = None
    autorisation_administrative: Optional[str] = None
    impact_environnemental: Optional[str] = None


class DragageUpdate(BaseModel):
    libelle: Optional[str] = None
    port_id: Optional[int] = None
    projet_id: Optional[int] = None
    type_dragage: Optional[TypeDragage] = None
    zone_traitee: Optional[str] = None
    superficie_draguee_m2: Optional[float] = None
    volume_mesure_m3: Optional[float] = None
    volume_facture_m3: Optional[float] = None
    profondeur_avant_m: Optional[float] = None
    profondeur_visee_m: Optional[float] = None
    profondeur_obtenue_m: Optional[float] = None
    nature_sediment: Optional[str] = None
    exutoire_rejet: Optional[str] = None
    autorisation_rejet_reference: Optional[str] = None
    entreprise: Optional[str] = None
    type_drague: Optional[str] = None
    cout_xaf: Optional[float] = None
    devise: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    jours_arret: Optional[int] = None
    statut: Optional[str] = None
    leve_bathymetrique_apres: Optional[bool] = None
    date_releve: Optional[date] = None
    autorisation_administrative: Optional[str] = None
    impact_environnemental: Optional[str] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None


class DragageOut(_Conf):
    id: int
    code_campagne: str
    libelle: str
    port_id: Optional[int] = None
    projet_id: Optional[int] = None
    type_dragage: Optional[TypeDragage] = None
    zone_traitee: Optional[str] = None
    superficie_draguee_m2: Optional[float] = None
    volume_mesure_m3: Optional[float] = None
    volume_facture_m3: Optional[float] = None
    profondeur_avant_m: Optional[float] = None
    profondeur_visee_m: Optional[float] = None
    profondeur_obtenue_m: Optional[float] = None
    nature_sediment: Optional[str] = None
    exutoire_rejet: Optional[str] = None
    autorisation_rejet_reference: Optional[str] = None
    entreprise: Optional[str] = None
    type_drague: Optional[str] = None
    cout_xaf: Optional[float] = None
    devise: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    jours_arret: Optional[int] = None
    statut: Optional[str] = None
    leve_bathymetrique_apres: Optional[bool] = None
    date_releve: Optional[date] = None
    autorisation_administrative: Optional[str] = None
    impact_environnemental: Optional[str] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# ─── 9. Autorisations administratives (EIES, permis) ─────────────────────────

class AutorisationTravauxCreate(_Provenance):
    reference: str = Field(min_length=2, max_length=80)
    type_autorisation: TypeAutorisationTravaux
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    administration: Optional[str] = None
    categorie_projet: Optional[str] = None
    objet: Optional[str] = None
    statut: StatutAutorisation = StatutAutorisation.EN_PREPARATION
    date_depot: Optional[date] = None
    date_accord: Optional[date] = None
    date_expiration: Optional[date] = None
    numero_arrete: Optional[str] = None
    conditions_particulieres: Optional[str] = None
    charges_enviro_xaf: Optional[float] = None
    audit_date_prochaine: Optional[date] = None
    piece_jointe: Optional[str] = None


class AutorisationTravauxUpdate(BaseModel):
    type_autorisation: Optional[TypeAutorisationTravaux] = None
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    administration: Optional[str] = None
    categorie_projet: Optional[str] = None
    objet: Optional[str] = None
    statut: Optional[StatutAutorisation] = None
    date_depot: Optional[date] = None
    date_accord: Optional[date] = None
    date_expiration: Optional[date] = None
    numero_arrete: Optional[str] = None
    conditions_particulieres: Optional[str] = None
    charges_enviro_xaf: Optional[float] = None
    audit_date_prochaine: Optional[date] = None
    piece_jointe: Optional[str] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    notes: Optional[str] = None


class AutorisationTravauxOut(_Conf):
    id: int
    reference: str
    type_autorisation: Optional[TypeAutorisationTravaux] = None
    projet_id: Optional[int] = None
    port_id: Optional[int] = None
    administration: Optional[str] = None
    categorie_projet: Optional[str] = None
    objet: Optional[str] = None
    statut: Optional[StatutAutorisation] = None
    date_depot: Optional[date] = None
    date_accord: Optional[date] = None
    date_expiration: Optional[date] = None
    numero_arrete: Optional[str] = None
    conditions_particulieres: Optional[str] = None
    charges_enviro_xaf: Optional[float] = None
    audit_date_prochaine: Optional[date] = None
    piece_jointe: Optional[str] = None
    source_reference: Optional[str] = None
    date_verification: Optional[date] = None
    auteur_saisie: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
