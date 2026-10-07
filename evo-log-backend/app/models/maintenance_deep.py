"""Modèles maintenance-industrielle (expansion wave 6).

Vise la couverture maximale du cycle de vie asset-intense :
  actif technique → composant → BOM → piece (catalogue OEM/aftermarket)
  → piece seriale singleton (moteur, roulement, courroie de distribution)
  → stock/mouvement → FMEA → plan préventif/condition → OT avec
  consommo pièces / labour / tools → RCA → overhaul → graissage →
  condition monitoring (vibration/thermo/huile) → prédiction → KPI fiabilité.

Chaque table porte company_id (multi-tenant) + index composites pour la
performance en production.
"""
from datetime import datetime, date
import enum
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum, Float, ForeignKey,
    Integer, Numeric, String, Table, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def _enum(name, values):
    """Enum SQLAlchemy stockant la VALEUR (str), pas le nom du membre."""
    members = {v.upper().replace("-", "_"): v for v in values}
    cls = enum.Enum(name, members, type=str)
    return cls, SAEnum(cls, name=name, values_callable=lambda e: [m.value for m in e])


# ---------------------------------------------------------------------------
# 1. ACTIF TECHNIQUE (racine hiérarchique)
# ---------------------------------------------------------------------------

class TechnicalAsset(Base):
    __tablename__ = "maint_technical_assets"
    __table_args__ = (
        UniqueConstraint("company_id", "tag_actif", name="uix_maint_assets_company_tag"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    tag_actif = Column(String(120), nullable=False, index=True)
    nom = Column(String(220), nullable=False)
    categorie = Column(String(120), nullable=True, index=True)  # grue STS / RTG / PM / reefer / pompe / camion
    sous_categorie = Column(String(120), nullable=True)
    module_source = Column(String(80), nullable=True, index=True)  # ferroviaire/port/magasin/transport/courier/...
    ref_entite_source = Column(String(120), nullable=True, index=True)  # id/tag de l'entité métier liée
    parent_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=True, index=True)
    emplacement = Column(String(220), nullable=True)
    fabricant = Column(String(180), nullable=True)
    modele = Column(String(180), nullable=True)
    numero_serie = Column(String(180), nullable=True, index=True)
    annee_fabrication = Column(Integer, nullable=True)
    date_mise_service = Column(Date, nullable=True, index=True)
    criticite = Column(String(30), nullable=True, index=True)  # A/B/C
    statut = Column(String(40), nullable=True, index=True)   # actif/en_panne/reforme/vendange
    cout_acquisition_xaf = Column(Numeric(18, 2), nullable=True)
    valeur_residuelle_xaf = Column(Numeric(18, 2), nullable=True)
    duree_vieutile_ans = Column(Integer, nullable=True)
    notes_techniques = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    parent = relationship("TechnicalAsset", remote_side=[id], backref="children")


# ---------------------------------------------------------------------------
# 2. COMPOSANT PRINCIPAL (moteur, boîte, hydraulique, roue...)
# ---------------------------------------------------------------------------

class AssetComponent(Base):
    __tablename__ = "maint_asset_components"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_id", "code_composant", name="uix_maint_comp"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    code_composant = Column(String(120), nullable=False, index=True)
    nom_composant = Column(String(220), nullable=False)
    type_composant = Column(String(120), nullable=True, index=True)  # moteur/transmission/hydraulique/freins/pneus/elec/structure
    ref_fabricant = Column(String(180), nullable=True, index=True)
    numero_serie = Column(String(180), nullable=True, index=True)
    nombre_pieces = Column(Integer, nullable=True)
    masse_kg = Column(Float, nullable=True)
    seuil_reforme = Column(String(220), nullable=True)
    criticite = Column(String(30), nullable=True)
    date_mise_service = Column(Date, nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    asset = relationship("TechnicalAsset", backref="components")


# ---------------------------------------------------------------------------
# 3. CATALOGUE PIÈCES DE RECHANGE (OEM, aftermarket, refus/retournement)
# ---------------------------------------------------------------------------

class SparePartCatalog(Base):
    __tablename__ = "maint_spare_part_catalog"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_interne", name="uix_maint_part_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_interne = Column(String(120), nullable=False, index=True)
    designation = Column(String(260), nullable=False)
    origine = Column(String(40), nullable=True, index=True)  # OEM / aftermarket / reconditionne
    ref_fabricant = Column(String(180), nullable=True, index=True)
    ref_essaiere_group = Column(String(180), nullable=True, index=True)
    categorie = Column(String(120), nullable=True, index=True)
    sous_categorie = Column(String(120), nullable=True)
    type_rechange = Column(String(60), nullable=True, index=True)  # critique/rechange standard/consommable
    unite_mesure = Column(String(40), nullable=True)              # piece/boite/litre/kg/metre
    unit_cost_xaf = Column(Numeric(18, 2), nullable=True)
    cost_achat_actuel_xaf = Column(Numeric(18, 2), nullable=True)
    fournisseur_principal_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=True, index=True)
    alternative_fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=True)
    delai_approvisionnement_j = Column(Integer, nullable=True)
    duree_vie_moyenne_h = Column(Integer, nullable=True)
    garantie_mois = Column(Integer, nullable=True)
    serialise_obligatoire = Column(Boolean, nullable=True)  # true → singleton tracé (ex. injecteur common-rail)
    poids_kg = Column(Float, nullable=True)
    volume_cm3 = Column(Integer, nullable=True)
    classification_hs = Column(String(40), nullable=True)   # position tarifaire douanière
    notes_techniques = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)


# ---------------------------------------------------------------------------
# 4. BILL OF MATERIAL (nomenclature asset → part, avec qté et position)
# ---------------------------------------------------------------------------

class BillOfMaterial(Base):
    __tablename__ = "maint_bill_of_material"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_id", "component_id", "part_id", "position_index",
                         name="uix_maint_bom"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    part_id = Column(Integer, ForeignKey("maint_spare_part_catalog.id"), nullable=False, index=True)
    position_index = Column(Integer, nullable=False)
    quantite_par_assemblage = Column(Float, nullable=True)
    unit = Column(String(40), nullable=True)
    niveau = Column(Integer, nullable=True, index=True)  # profondeur dans l'arbre BOM
    level_parent_id = Column(Integer, ForeignKey("maint_bill_of_material.id"), nullable=True, index=True)
    obligatoire = Column(Boolean, nullable=True)
    remplacement_interval = Column(String(120), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="bom")
    component = relationship("AssetComponent", backref="bom_entries")
    part = relationship("SparePartCatalog", backref="bom_entries")


# ---------------------------------------------------------------------------
# 5. PIÈCE SÉRIALISÉE (singleton, une unité = une ligne avec suivi propre)
# ---------------------------------------------------------------------------

class SerializedPart(Base):
    __tablename__ = "maint_serialized_parts"
    __table_args__ = (
        UniqueConstraint("company_id", "numero_serial", name="uix_maint_serialized_part"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("maint_spare_part_catalog.id"), nullable=False, index=True)
    numero_serial = Column(String(180), nullable=False, index=True)
    numero_lot = Column(String(120), nullable=True, index=True)
    date_fabrication = Column(Date, nullable=True)
    date_reception = Column(Date, nullable=True, index=True)
    date_mise_service = Column(Date, nullable=True, index=True)
    date_reforme = Column(Date, nullable=True, index=True)
    cycles_utilisation = Column(Integer, nullable=True)
    heures_utilisees = Column(Float, nullable=True)
    kilometres_utilises = Column(Float, nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    # stockage: en stock / en attente / installe / recondiionne / rebut / retour fabricant
    asset_id_actuel = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=True, index=True)
    composant_id_actuel = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    emplacement_stock = Column(String(220), nullable=True)
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=True, index=True)
    numero_bl_achat = Column(String(120), nullable=True, index=True)
    numero_facture_achat = Column(String(120), nullable=True, index=True)
    date_garantie_fin = Column(Date, nullable=True)
    valeur_achat_xaf = Column(Numeric(18, 2), nullable=True)
    hashs_certificat = Column(Text, nullable=True)  # JSON [{type,url,sha256}]
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    part = relationship("SparePartCatalog", backref="serialized_units")
    asset = relationship("TechnicalAsset", foreign_keys=[asset_id_actuel], backref="serialized_parts_installed")
    component = relationship("AssetComponent", foreign_keys=[composant_id_actuel], backref="serialized_parts_installed")


# ---------------------------------------------------------------------------
# 6. STOCK PIÈCES par magasin/entrepôt
# ---------------------------------------------------------------------------

class PartInventory(Base):
    __tablename__ = "maint_part_inventory"
    __table_args__ = (
        UniqueConstraint("company_id", "part_id", "magasin_id", "emplacement", name="uix_maint_part_inv"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("maint_spare_part_catalog.id"), nullable=False, index=True)
    magasin_id = Column(Integer, ForeignKey("entrepots.id"), nullable=True, index=True)
    emplacement = Column(String(180), nullable=True, index=True)
    quantite_en_stock = Column(Integer, nullable=False, default=0)
    quantite_reservee = Column(Integer, nullable=True, default=0)
    quantite_min = Column(Integer, nullable=True, index=True)
    quantite_max = Column(Integer, nullable=True)
    point_commande = Column(Integer, nullable=True)
    cout_moyen_pondere_xaf = Column(Numeric(18, 2), nullable=True)
    valeur_totale_xaf = Column(Numeric(18, 2), nullable=True)
    date_dernier_mouvement = Column(DateTime(timezone=True), nullable=True, index=True)
    date_dernier_inventaire = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    part = relationship("SparePartCatalog", backref="inventory_lines")


# ---------------------------------------------------------------------------
# 7. MOUVEMENT DE PIÈCE (entrée, sortie, transfert, adjustment, retour)
# ---------------------------------------------------------------------------

class PartMovement(Base):
    __tablename__ = "maint_part_movements"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_mouvement", name="uix_maint_part_mvmt"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_mouvement = Column(String(140), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("maint_spare_part_catalog.id"), nullable=False, index=True)
    serialized_part_id = Column(Integer, ForeignKey("maint_serialized_parts.id"), nullable=True, index=True)
    type_mouvement = Column(String(40), nullable=False, index=True)
    # entree_achat / sortie_ot / retour_garantie / transfert / adjustment / rebut / inventaire
    quantite = Column(Float, nullable=False)
    magasin_source_id = Column(Integer, ForeignKey("entrepots.id"), nullable=True, index=True)
    magasin_destination_id = Column(Integer, ForeignKey("entrepots.id"), nullable=True, index=True)
    work_order_id = Column(Integer, ForeignKey("maint_work_orders.id"), nullable=True, index=True)
    bon_livraison_id = Column(Integer, nullable=True, index=True)  # lien vers BL achat si entree
    facture_achat_id = Column(Integer, nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    date_mouvement = Column(DateTime(timezone=True), nullable=False, index=True)
    valeur_xaf = Column(Numeric(18, 2), nullable=True)
    motif = Column(String(220), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    part = relationship("SparePartCatalog", backref="movements")
    serialized = relationship("SerializedPart", backref="movements")


# ---------------------------------------------------------------------------
# 8. MODE DE DÉFAILLANCE (FMEA)
# ---------------------------------------------------------------------------

class FailureMode(Base):
    __tablename__ = "maint_failure_modes"
    __table_args__ = (
        UniqueConstraint("company_id", "code_fmea", name="uix_maint_fmea_code"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_fmea = Column(String(120), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=True, index=True)
    component_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    fonction = Column(String(220), nullable=True)
    mode_defaillance = Column(String(280), nullable=False)
    mecanisme = Column(String(180), nullable=True)  # fatigue / corrosion / usure / electrique / surcharge
    causes = Column(Text, nullable=True)             # liste JSON [{cause, proba}]
    effets = Column(Text, nullable=True)
    gravite = Column(Integer, nullable=True, index=True)   # 1-10
    occurrence = Column(Integer, nullable=True, index=True) # 1-10
    detection = Column(Integer, nullable=True, index=True)  # 1-10
    ipr = Column(Integer, nullable=True, index=True)         # index priorité risque = G*O*D
    methode_detection = Column(String(220), nullable=True)
    actions_preventives = Column(Text, nullable=True)
    actions_correctives = Column(Text, nullable=True)
    responsable = Column(String(180), nullable=True)
    date_evaluation = Column(Date, nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    asset = relationship("TechnicalAsset", backref="failure_modes")
    component = relationship("AssetComponent", backref="failure_modes")


# ---------------------------------------------------------------------------
# 9. PLAN DE MAINTENANCE (preventif / conditionnel / predictif)
# ---------------------------------------------------------------------------

class MaintenancePlan(Base):
    __tablename__ = "maint_maintenance_plans"
    __table_args__ = (
        UniqueConstraint("company_id", "code_plan", name="uix_maint_plan_code"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_plan = Column(String(120), nullable=False, index=True)
    nom = Column(String(220), nullable=False)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=True, index=True)
    component_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    type_plan = Column(String(40), nullable=False, index=True)
    # preventif_periodique / conditionnel / predictif / reglementaire
    frequence_type = Column(String(40), nullable=True, index=True)   # calendaire/heures/km/cycle
    frequence_valeur = Column(Float, nullable=True)
    frequence_unite = Column(String(40), nullable=True)              # jour/mois/an/heure/km/cycle
    seuil_declenchement = Column(String(180), nullable=True)
    prochaine_echeance = Column(Date, nullable=True, index=True)
    duree_estimee_h = Column(Float, nullable=True)
    criticite = Column(String(30), nullable=True, index=True)
    cout_estime_par_cycle_xaf = Column(Numeric(18, 2), nullable=True)
    skills_requis = Column(String(220), nullable=True)
    outillage_requis = Column(Text, nullable=True)
    pieces_cle = Column(Text, nullable=True)  # JSON [{part_id, qte}]
    version = Column(Integer, nullable=True, default=1)
    statut = Column(String(40), nullable=True, index=True)  # actif/suspendu/obsolete
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    asset = relationship("TechnicalAsset", backref="plans")


# ---------------------------------------------------------------------------
# 10. TÂCHE ATOMIQUE de maintenance
# ---------------------------------------------------------------------------

class MaintenanceTask(Base):
    __tablename__ = "maint_maintenance_tasks"
    __table_args__ = (
        UniqueConstraint("company_id", "code_tache", name="uix_maint_task_code"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_tache = Column(String(120), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("maint_maintenance_plans.id"), nullable=True, index=True)
    titre = Column(String(220), nullable=False)
    description_geste = Column(Text, nullable=True)
    duree_estimee_min = Column(Integer, nullable=True)
    nb_techniciens = Column(Integer, nullable=True)
    competence_requise = Column(String(180), nullable=True)
    niveau_habiliture = Column(String(120), nullable=True)
    epi_requis = Column(String(220), nullable=True)
    outillage = Column(Text, nullable=True)
    couples_re_serrage = Column(String(220), nullable=True)
    pieces_requises = Column(Text, nullable=True)  # JSON [{part_id, qte}]
    ordre_execution = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    plan = relationship("MaintenancePlan", backref="tasks")


# ---------------------------------------------------------------------------
# 11. ORDRE DE TRAVAIL (OT)
# ---------------------------------------------------------------------------

class WorkOrder(Base):
    __tablename__ = "maint_work_orders"
    __table_args__ = (
        UniqueConstraint("company_id", "numero_ot", name="uix_maint_wo_numero"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    numero_ot = Column(String(120), nullable=False, index=True)
    type_ot = Column(String(40), nullable=False, index=True)
    # preventif / curatif / evolutif / correctif_ameliore / controle_reglementaire / inspection
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    plan_id = Column(Integer, ForeignKey("maint_maintenance_plans.id"), nullable=True, index=True)
    defaillance_id = Column(Integer, ForeignKey("maint_asset_failures.id"), nullable=True, index=True)
    titre = Column(String(220), nullable=False)
    description = Column(Text, nullable=True)
    priorite = Column(String(30), nullable=True, index=True)  # P1/P2/P3/P4
    criticite_asset = Column(String(30), nullable=True)
    date_detection = Column(DateTime(timezone=True), nullable=True, index=True)
    date_ouverture = Column(DateTime(timezone=True), nullable=True, index=True)
    date_prevue_debut = Column(DateTime(timezone=True), nullable=True, index=True)
    date_prevue_fin = Column(DateTime(timezone=True), nullable=True, index=True)
    date_reel_debut = Column(DateTime(timezone=True), nullable=True, index=True)
    date_reel_fin = Column(DateTime(timezone=True), nullable=True, index=True)
    statut = Column(String(40), nullable=True, index=True)
    # brouillon / planifie / en_attente_pieces / en_cours / en_test / cloture / annule
    technicien_principal_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    prestataire_id = Column(Integer, ForeignKey("prestataires.id"), nullable=True, index=True)
    heures_prevues = Column(Float, nullable=True)
    heures_reelles = Column(Float, nullable=True)
    cout_pieces_xaf = Column(Numeric(18, 2), nullable=True)
    cout_main_oeuvre_xaf = Column(Numeric(18, 2), nullable=True)
    cout_prestataire_xaf = Column(Numeric(18, 2), nullable=True)
    cout_total_xaf = Column(Numeric(18, 2), nullable=True)
    cause_racine_id = Column(Integer, ForeignKey("maint_root_causes.id"), nullable=True, index=True)
    arret_production = Column(Boolean, nullable=True)
    impact_securite = Column(Boolean, nullable=True)
    compte_rendu = Column(Text, nullable=True)
    pieces_ressorties = Column(Text, nullable=True)
    photos_url = Column(Text, nullable=True)  # JSON [urls S3/MinIO]
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="work_orders")


# ---------------------------------------------------------------------------
# 11 bis. DÉCLARATION DE PANNE (événement à l'origine d'un OT curatif)
# ---------------------------------------------------------------------------

class AssetFailure(Base):
    __tablename__ = "maint_asset_failures"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_defaillance", name="uix_maint_def_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_defaillance = Column(String(120), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    mode_id = Column(Integer, ForeignKey("maint_failure_modes.id"), nullable=True, index=True)
    date_detection = Column(DateTime(timezone=True), nullable=False, index=True)
    detecteur = Column(String(180), nullable=True)  # operateur / capteur / inspection
    source_signalement = Column(String(80), nullable=True)
    severite = Column(String(30), nullable=True, index=True)
    description = Column(Text, nullable=True)
    symptomes = Column(Text, nullable=True)
    code_defaut = Column(String(120), nullable=True, index=True)  # OBD / fault code machine
    heures_arret = Column(Float, nullable=True)
    cout_indirect_xaf = Column(Numeric(18, 2), nullable=True)
    statut = Column(String(40), nullable=True, index=True)  # ouverte/en_cours/resolue/contournement
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="failures")
    mode = relationship("FailureMode", backref="failures")


# ---------------------------------------------------------------------------
# 12. PIÈCE CONSOMMÉE SUR UN OT
# ---------------------------------------------------------------------------

class WorkOrderPart(Base):
    __tablename__ = "maint_work_order_parts"
    __table_args__ = (
        UniqueConstraint("company_id", "work_order_id", "part_id", "serialized_part_id", name="uix_maint_wo_part"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("maint_work_orders.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("maint_spare_part_catalog.id"), nullable=False, index=True)
    serialized_part_id = Column(Integer, ForeignKey("maint_serialized_parts.id"), nullable=True, index=True)
    quantite_demandee = Column(Float, nullable=False)
    quantite_livree = Column(Float, nullable=True)
    quantite_consommee = Column(Float, nullable=True)
    quantite_retour = Column(Float, nullable=True)
    valeur_xaf = Column(Numeric(18, 2), nullable=True)
    date_sortie = Column(DateTime(timezone=True), nullable=True, index=True)
    motif_retour = Column(String(220), nullable=True)
    magasin_id = Column(Integer, ForeignKey("entrepots.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    work_order = relationship("WorkOrder", backref="consumed_parts")
    part = relationship("SparePartCatalog", backref="wo_usages")
    serialized = relationship("SerializedPart", backref="wo_usages")


# ---------------------------------------------------------------------------
# 13. MAIN-D'OEUVRE sur OT
# ---------------------------------------------------------------------------

class WorkOrderLabour(Base):
    __tablename__ = "maint_work_order_labours"
    __table_args__ = (
        UniqueConstraint("company_id", "work_order_id", "user_id", "date_travail", name="uix_maint_wo_labour"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("maint_work_orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_intervenant = Column(String(120), nullable=True)  # technicien/chef/habilite_electrique
    date_travail = Column(Date, nullable=False, index=True)
    heures_prevues = Column(Float, nullable=True)
    heures_reelles = Column(Float, nullable=False)
    taux_horaire_xaf = Column(Numeric(18, 2), nullable=True)
    cout_total_xaf = Column(Numeric(18, 2), nullable=True)
    statut = Column(String(40), nullable=True, index=True)  # planifie/intervenu/valide
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    work_order = relationship("WorkOrder", backref="labour_lines")
    user = relationship("User", backref="maint_labour_lines")


# ---------------------------------------------------------------------------
# 14. OUTILLAGE requis pour OT
# ---------------------------------------------------------------------------

class WorkOrderTool(Base):
    __tablename__ = "maint_work_order_tools"
    __table_args__ = (
        UniqueConstraint("company_id", "work_order_id", "reference_outillage", name="uix_maint_wo_tool"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("maint_work_orders.id"), nullable=False, index=True)
    reference_outillage = Column(String(180), nullable=False, index=True)
    designation = Column(String(220), nullable=True)
    type_outillage = Column(String(80), nullable=True, index=True)  # mesure / levage / coupe / securite
    proprietaire = Column(String(120), nullable=True)               # interne / externe (location)
    numero_inventaire = Column(String(180), nullable=True, index=True)
    date_pret_debut = Column(Date, nullable=True)
    date_pret_fin = Column(Date, nullable=True)
    date_calibration = Column(Date, nullable=True)
    cout_location_xaf = Column(Numeric(18, 2), nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    work_order = relationship("WorkOrder", backref="tools_required")


# ---------------------------------------------------------------------------
# 15. ANALYSE DE CAUSE RACINE
# ---------------------------------------------------------------------------

class RootCauseAnalysis(Base):
    __tablename__ = "maint_root_causes"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_rca", name="uix_maint_rca_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_rca = Column(String(120), nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("maint_work_orders.id"), nullable=True, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=True, index=True)
    methode = Column(String(80), nullable=True, index=True)  # 5_pourquoi / ishikawa / arbre_defaut / fault_tree
    probleme = Column(Text, nullable=False)
    pourquoi_1 = Column(Text, nullable=True)
    pourquoi_2 = Column(Text, nullable=True)
    pourquoi_3 = Column(Text, nullable=True)
    pourquoi_4 = Column(Text, nullable=True)
    pourquoi_5 = Column(Text, nullable=True)
    categories_ishikawa = Column(Text, nullable=True)  # JSON 5M
    cause_racine = Column(Text, nullable=True)
    causes_contributives = Column(Text, nullable=True)
    actions_correctives = Column(Text, nullable=True)
    actions_preventives_globales = Column(Text, nullable=True)
    responsable_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    date_cloture = Column(Date, nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    work_order = relationship("WorkOrder", foreign_keys=[work_order_id], backref="rca")


# ---------------------------------------------------------------------------
# 16. CAMPAGNE DE RÉVISION GÉNÉRALE (overhaul / gros entretien)
# ---------------------------------------------------------------------------

class OverhaulCampaign(Base):
    __tablename__ = "maint_overhaul_campaigns"
    __table_args__ = (
        UniqueConstraint("company_id", "code_overhaul", name="uix_maint_overhaul_code"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_overhaul = Column(String(120), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    type_overhaul = Column(String(60), nullable=True, index=True)  # mineur / majeur / moteur / transmission
    intervalle_heures = Column(Float, nullable=True)
    intervalle_km = Column(Float, nullable=True)
    intervalle_mois = Column(Integer, nullable=True)
    prochaine_echeance_date = Column(Date, nullable=True, index=True)
    prochaine_echeance_heures = Column(Float, nullable=True)
    prestataire_id = Column(Integer, ForeignKey("prestataires.id"), nullable=True, index=True)
    budget_estime_xaf = Column(Numeric(18, 2), nullable=True)
    date_debut = Column(Date, nullable=True, index=True)
    date_fin = Column(Date, nullable=True)
    duree_reelle_j = Column(Integer, nullable=True)
    kits_pieces_utilises = Column(Text, nullable=True)
    rapport_technique = Column(Text, nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="overhauls")


# ---------------------------------------------------------------------------
# 17. PLAN DE GRAISSAGE / LUBRIFICATION
# ---------------------------------------------------------------------------

class LubricationSchedule(Base):
    __tablename__ = "maint_lubrication_schedules"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_id", "point_lubrifiant", name="uix_maint_lubri_point"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    point_lubrifiant = Column(String(120), nullable=False, index=True)
    type_lubrifiant = Column(String(120), nullable=True)
    grade = Column(String(80), nullable=True)   # ISO VG 68 / SAE 15W-40 / NLG 2
    marque = Column(String(120), nullable=True)
    quantite_litre = Column(Float, nullable=True)
    quantite_gramme = Column(Float, nullable=True)
    frequence_heures = Column(Float, nullable=True)
    frequence_jours = Column(Integer, nullable=True)
    prochaine_date = Column(Date, nullable=True, index=True)
    methode = Column(String(120), nullable=True)  # manuelle / centralisee / brouillard
    statut = Column(String(40), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="lubrications")


# ---------------------------------------------------------------------------
# 18. SURVEILLANCE CONDITION (vibration / thermo / huile / ultrason)
# ---------------------------------------------------------------------------

class ConditionReading(Base):
    __tablename__ = "maint_condition_readings"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_lecture", name="uix_maint_cond_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_lecture = Column(String(140), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    type_technique = Column(String(60), nullable=False, index=True)
    # vibration / thermographie / analyse_huile / ultrason / courant_moteur
    capteur_id = Column(Integer, ForeignKey("maint_sensors.id"), nullable=True, index=True)
    point_mesure = Column(String(180), nullable=True)
    date_lecture = Column(DateTime(timezone=True), nullable=False, index=True)
    valeur_principale = Column(Float, nullable=True, index=True)
    unite = Column(String(60), nullable=True)  # mm/s rms / °C / ppm / dB
    seuil_alerte = Column(Float, nullable=True)
    seuil_critical = Column(Float, nullable=True)
    statut_resultat = Column(String(40), nullable=True, index=True)
    # normal / alerte / critique / tendance_hausse / tendance_baisse
    spectre_url = Column(String(280), nullable=True)  # image / CSV stocké
    analyse_experte = Column(Text, nullable=True)
    operateur = Column(String(180), nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="condition_readings")


# ---------------------------------------------------------------------------
# 18 bis. CAPTEUR IoT de surveillance
# ---------------------------------------------------------------------------

class Sensor(Base):
    __tablename__ = "maint_sensors"
    __table_args__ = (
        UniqueConstraint("company_id", "code_capteur", name="uix_maint_sensor_code"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_capteur = Column(String(120), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=True, index=True)
    composant_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    type_capteur = Column(String(80), nullable=True, index=True)  # accelero / thermo / pression / niveau / courant
    protocol = Column(String(60), nullable=True)                   # Modbus / MQTT / OPC-UA / LoRa
    adresse_mqtt = Column(String(220), nullable=True)
    url_flux = Column(String(280), nullable=True)
    frequence_echantillonnage_hz = Column(Integer, nullable=True)
    resolution_bits = Column(Integer, nullable=True)
    unite_sortie = Column(String(60), nullable=True)
    plage_min = Column(Float, nullable=True)
    plage_max = Column(Float, nullable=True)
    seuil_alerte_bas = Column(Float, nullable=True)
    seuil_alerte_haut = Column(Float, nullable=True)
    calibration_periodicite_mois = Column(Integer, nullable=True)
    derniere_calibration = Column(Date, nullable=True)
    fabricant = Column(String(180), nullable=True)
    modele = Column(String(180), nullable=True)
    numero_serie = Column(String(180), nullable=True, index=True)
    statut = Column(String(40), nullable=True, index=True)  # actif/en_panne/hors_ligne/remplace
    date_installation = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="sensors")


# ---------------------------------------------------------------------------
# 19. MODÈLE PRÉDICTIF (MTTF, seuil d'alerte, ML)
# ---------------------------------------------------------------------------

class PredictiveModel(Base):
    __tablename__ = "maint_predictive_models"
    __table_args__ = (
        UniqueConstraint("company_id", "code_modele", name="uix_maint_pred_model"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_modele = Column(String(120), nullable=False, index=True)
    nom = Column(String(220), nullable=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=True, index=True)
    composant_id = Column(Integer, ForeignKey("maint_asset_components.id"), nullable=True, index=True)
    type_modele = Column(String(80), nullable=True, index=True)
    # weibull / bayesien / regression / random_forest / reseau_de_neurones / seuil_statique
    variable_entree = Column(String(220), nullable=True)   # ex 'vibration_rms, temperature, courant'
    variable_sortie = Column(String(180), nullable=True)
    heuristique = Column(Text, nullable=True)
    precision_pct = Column(Float, nullable=True)
    rappel_pct = Column(Float, nullable=True)
    auc = Column(Float, nullable=True)
    version = Column(String(60), nullable=True)
    date_entrainement = Column(Date, nullable=True)
    date_debut_production = Column(Date, nullable=True)
    seuil_declenchement_ot = Column(Float, nullable=True)
    statut = Column(String(40), nullable=True, index=True)  # dev/valide/actif/rejete
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 20. KPI FIABILITÉ (MTBF / MTTR / dispo) agrégé par asset/mois
# ---------------------------------------------------------------------------

class ReliabilityKpi(Base):
    __tablename__ = "maint_reliability_kpis"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_id", "periode", name="uix_maint_reli_kpi"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    periode = Column(String(10), nullable=False, index=True)  # 2026-09 (YYYY-MM)
    nb_defaillances = Column(Integer, nullable=True)
    nb_ot_preventif = Column(Integer, nullable=True)
    nb_ot_curatif = Column(Integer, nullable=True)
    heures_fonctionnement = Column(Float, nullable=True)
    heures_arret = Column(Float, nullable=True)
    mtbf_heures = Column(Float, nullable=True, index=True)  # Mean Time Between Failures
    mttr_heures = Column(Float, nullable=True, index=True)  # Mean Time To Repair
    mttf_heures = Column(Float, nullable=True)
    disponibilite_pct = Column(Float, nullable=True, index=True)
    cout_maintenance_xaf = Column(Numeric(18, 2), nullable=True)
    cout_indirect_arret_xaf = Column(Numeric(18, 2), nullable=True)
    oee_pct = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="reliability_kpis")


# ---------------------------------------------------------------------------
# 21. CONTRÔLE RÉGLEMENTAIRE (grue / ascenseur / pressostat / EC)
# ---------------------------------------------------------------------------

class RegulatoryInspection(Base):
    __tablename__ = "maint_regulatory_inspections"
    __table_args__ = (
        UniqueConstraint("company_id", "numero_pv", name="uix_maint_reg_pv"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    numero_pv = Column(String(120), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    type_controle = Column(String(120), nullable=True, index=True)
    autorite = Column(String(180), nullable=True, index=True)  # ANINF / Inspection Travail / APN / MINMT
    organisme_controle = Column(String(180), nullable=True)    # Bureau Veritas / Socotec / Apave
    date_controle = Column(Date, nullable=True, index=True)
    date_validite = Column(Date, nullable=True, index=True)
    resultat = Column(String(60), nullable=True, index=True)  # conforme / avec_reserve / non_conforme
    observations = Column(Text, nullable=True)
    pv_url = Column(String(280), nullable=True)
    prochaine_echeance = Column(Date, nullable=True, index=True)
    inspecteur = Column(String(180), nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="reg_inspections")


# ---------------------------------------------------------------------------
# 22. BUDGET MAINTENANCE par asset/année
# ---------------------------------------------------------------------------

class MaintenanceBudget(Base):
    __tablename__ = "maint_maintenance_budgets"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_id", "exercice", name="uix_maint_budget_asset_year"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("maint_technical_assets.id"), nullable=False, index=True)
    exercice = Column(String(8), nullable=False, index=True)
    budget_prevu_pieces_xaf = Column(Numeric(18, 2), nullable=True)
    budget_prevu_main_oeuvre_xaf = Column(Numeric(18, 2), nullable=True)
    budget_prevu_prestataire_xaf = Column(Numeric(18, 2), nullable=True)
    budget_total_prevu_xaf = Column(Numeric(18, 2), nullable=True)
    consomme_pieces_xaf = Column(Numeric(18, 2), nullable=True)
    consomme_main_oeuvre_xaf = Column(Numeric(18, 2), nullable=True)
    consomme_prestataire_xaf = Column(Numeric(18, 2), nullable=True)
    total_consomme_xaf = Column(Numeric(18, 2), nullable=True)
    ecart_pct = Column(Float, nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    asset = relationship("TechnicalAsset", foreign_keys=[asset_id], backref="budgets")


# ---------------------------------------------------------------------------
# 23. FOURNISSEUR / PRESTATAIRE HABILITÉ MAINTENANCE
# ---------------------------------------------------------------------------

class MaintenanceVendor(Base):
    __tablename__ = "maint_maintenance_vendors"
    __table_args__ = (
        UniqueConstraint("company_id", "code_prestataire", name="uix_maint_vendor_code"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_prestataire = Column(String(120), nullable=False, index=True)
    raison_sociale = Column(String(220), nullable=False)
    pays = Column(String(80), nullable=True)
    specialites = Column(String(280), nullable=True)
    habilitations = Column(Text, nullable=True)   # JSON [{type, autorite, valide_jusqu}]
    certifications_iso = Column(String(280), nullable=True)
    contact_nom = Column(String(180), nullable=True)
    contact_email = Column(String(180), nullable=True)
    contact_telephone = Column(String(60), nullable=True)
    delai_reponse_h = Column(Integer, nullable=True)
    astreinte_247 = Column(Boolean, nullable=True)
    zone_intervention = Column(String(280), nullable=True)
    tarif_horaire_xaf = Column(Numeric(18, 2), nullable=True)
    note_satisfaction = Column(Float, nullable=True)  # 1-5
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)
