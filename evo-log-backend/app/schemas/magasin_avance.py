"""Pydantic schemas for advanced warehouse module"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# Peremption schemas
class PeremptionBase(BaseModel):
    date_peremption: date
    lot_numero: str
    numero_serie: Optional[str] = None


class PeremptionCreate(PeremptionBase):
    stock_id: int


class PeremptionResponse(PeremptionBase):
    id: int
    stock_id: int
    
    class Config:
        from_attributes = True


# ReservationStock schemas
class ReservationStockBase(BaseModel):
    stock_id: int
    type_reservation: str
    reference_id: int
    quantite: float
    date_expiration: Optional[date] = None


class ReservationStockCreate(ReservationStockBase):
    pass


class ReservationStockResponse(ReservationStockBase):
    id: int
    date_reservation: datetime
    statut: str
    date_liberation: Optional[datetime] = None
    date_consommation: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# KitArticle schemas
class KitArticleBase(BaseModel):
    article_kit_id: int
    nom_kit: str
    description: str


class KitArticleCreate(KitArticleBase):
    pass


class KitArticleResponse(KitArticleBase):
    id: int
    
    class Config:
        from_attributes = True


class ComposantKitBase(BaseModel):
    kit_id: int
    article_composant_id: int
    quantite: float


class ComposantKitCreate(ComposantKitBase):
    pass


class ComposantKitResponse(ComposantKitBase):
    id: int
    
    class Config:
        from_attributes = True


# EmplacementDetail schemas
class EmplacementDetailBase(BaseModel):
    entrepot_id: int
    zone: str
    allee: str
    rack: Optional[str] = None
    casier: Optional[str] = None
    niveau: Optional[str] = None


class EmplacementDetailCreate(EmplacementDetailBase):
    pass


class EmplacementDetailResponse(EmplacementDetailBase):
    id: int
    
    class Config:
        from_attributes = True


# TransfertStock schemas
class TransfertStockBase(BaseModel):
    stock_id: int
    entrepot_source_id: int
    entrepot_destination_id: int
    quantite: float
    motif: str
    date_transfert: Optional[date] = None


class TransfertStockCreate(TransfertStockBase):
    pass


class TransfertStockResponse(TransfertStockBase):
    id: int
    statut: str
    date_execution: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# InventaireTournant schemas — Batch 18 : ALIGNES SUR LE MODELE REEL
# (app/models/magasin_avance.InventaireTournant). L'ancien schema inventait
# date_inventaire / validateur_id / date_validation : colonnes qui n'existent
# PAS (reel : date_debut, date_fin, responsable, notes) → TypeError 500 garanti
# a la creation. numero_inventaire (unique NOT NULL) est genere cote route.
class InventaireTournantBase(BaseModel):
    entrepot_id: int
    date_debut: date
    date_fin: Optional[date] = None
    # colonne nullable sur le modèle → None admis à la lecture, jamais
    # transformé en chaîne inventée
    type_inventaire: Optional[str] = "tournant"  # partiel, complet, cyclique
    notes: Optional[str] = None


class InventaireTournantCreate(InventaireTournantBase):
    pass


class InventaireTournantResponse(InventaireTournantBase):
    id: int
    numero_inventaire: str
    statut: str  # planifie, en_cours, termine, annule
    responsable: Optional[int] = None

    class Config:
        from_attributes = True


class LigneInventaireCreate(BaseModel):
    # compteur_id (fantome) → operateur (colonne reelle)
    stock_id: int
    quantite_comptee: float
    operateur: Optional[int] = None
    commentaires: Optional[str] = None


class LigneInventaireResponse(BaseModel):
    id: int
    inventaire_id: int
    stock_id: int
    quantite_theorique: Optional[float] = None
    quantite_comptee: Optional[float] = None
    ecart: Optional[float] = None
    statut: str
    operateur: Optional[int] = None
    date_comptage: Optional[date] = None  # colonne reelle de type Date
    commentaires: Optional[str] = None

    class Config:
        from_attributes = True


# FournisseurStock schemas — Batch 18 : alignés sur le modèle réel
# (delai_livraison_jours/qualite/fiabilite étaient des fantaisies : le modèle
# porte delai_moyen_livraison, taux_livraison_ponctuelle, qualite_produit,
# prix_competitif, service_client, note_globale).
class FournisseurStockCreate(BaseModel):
    fournisseur_id: int
    delai_moyen_livraison: Optional[int] = None  # jours
    taux_livraison_ponctuelle: Optional[float] = None  # %
    qualite_produit: Optional[float] = None  # note 1-10
    prix_competitif: Optional[float] = None  # note 1-10
    service_client: Optional[float] = None  # note 1-10
    note_globale: Optional[float] = None  # calculée si absent
    commentaires: Optional[str] = None


class FournisseurStockResponse(FournisseurStockCreate):
    id: int
    date_evaluation: Optional[date] = None
    evaluateur: Optional[int] = None
    statut: str

    class Config:
        from_attributes = True


# CommandeFournisseur / LigneCommandeFournisseur schemas — SUPPRIMÉS
# (Batch 18) : squelettes fantômes jamais consommés par aucune route
# (reference, date_prevue, date_livraison, article_id n'existent pas ; le
# modèle réel porte numero_commande, date_livraison_prevue,
# date_livraison_reelle, stock_id). Utilisés uniquement par la route
# /reapprovisionnement/automatique qui les construit sur le modèle réel.


# BonReception schemas — Batch 19 : ALIGNES SUR LE MODELE REEL
# (app/models/magasin_avance.BonReception). L'ancien schema inventait
# commande_id (reel : commande_fournisseur_id), imposait date_reception et
# un statut "en_cours" hors workflow reel (en_attente/valide/refuse) ; le
# numero_bon (unique NOT NULL) etait oublie → TypeError 500 garanti.
# Numero BR-YYYYMMDD-NNNN genere cote route.
class BonReceptionCreate(BaseModel):
    fournisseur_id: int
    entrepot_id: int
    commande_fournisseur_id: Optional[int] = None
    date_reception: Optional[date] = None  # defaut = aujourd'hui cote route
    notes: Optional[str] = None


class BonReceptionUpdate(BaseModel):
    # statut jamais modifiable ici — transitions uniquement via /valider
    fournisseur_id: Optional[int] = None
    entrepot_id: Optional[int] = None
    date_reception: Optional[date] = None
    notes: Optional[str] = None


class BonReceptionResponse(BaseModel):
    id: int
    numero_bon: str
    commande_fournisseur_id: Optional[int] = None
    fournisseur_id: int
    entrepot_id: int
    date_reception: Optional[date] = None
    operateur: Optional[int] = None
    validateur: Optional[int] = None
    date_validation: Optional[date] = None  # colonne reelle de type Date
    statut: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# LigneBonReception schemas — Batch 19 : le fantaisiste
# (bon_id, article_id, emplacement_id) remplace par les colonnes reelles
# (bon_reception_id, stock_id, emplacement en String). quantite_commandee
# n'est plus obligatoire (NULL admis si réception sans commande).
class LigneBonReceptionCreate(BaseModel):
    stock_id: int
    quantite_recue: float
    quantite_commandee: Optional[float] = None
    prix_unitaire: Optional[float] = None
    emplacement: Optional[str] = None
    numero_lot: Optional[str] = None
    date_peremption: Optional[date] = None
    commentaires: Optional[str] = None


class LigneBonReceptionResponse(BaseModel):
    id: int
    bon_reception_id: int
    stock_id: int
    quantite_recue: float
    quantite_commandee: Optional[float] = None
    prix_unitaire: Optional[float] = None
    emplacement: Optional[str] = None
    numero_lot: Optional[str] = None
    date_peremption: Optional[date] = None
    statut: str
    commentaires: Optional[str] = None

    class Config:
        from_attributes = True


# BonSortie schemas — SUPPRIMÉS (Batch 16) : squelettes fantômes déconnectés du
# modèle réel (destinataire_id, bon_id, quantite n'existent pas sur
# BonSortie/LigneBonSortie ; stock.quantite non plus). Les VRAIS schémas du bon
# de sortie vivent dans app/schemas/removal_slip.py (route live
# /api/v1/magasin/removal-slips).


# RetourClient schemas — Batch 17 : ALIGNES SUR LE MODELE REEL
# (app/models/magasin_avance.RetourClient). Les anciens squelettes inventaient
# article_id / etat / action_effectuee / date_traitement : champs qui
# n'existent PAS sur le modele → TypeError 500 a la creation, perte silencieuse
# au traitement. Le numero de retour est genere cote route (RT-YYYYMMDD-NNNN).
class RetourClientCreate(BaseModel):
    client_id: int
    bon_sortie_id: Optional[int] = None
    type_retour: Optional[str] = None  # defectif, mauvais_quantite, refus, erreur_livraison
    motif: str
    quantite: Optional[float] = None
    notes: Optional[str] = None


class RetourClientUpdate(BaseModel):
    type_retour: Optional[str] = None
    motif: Optional[str] = None
    quantite: Optional[float] = None
    notes: Optional[str] = None


class RetourClientTraitement(BaseModel):
    decision: str  # accepte | refuse
    action: Optional[str] = None  # obligatoire si accepte: remplacement|remboursement|destruction
    cout_traitement: Optional[float] = None
    notes: Optional[str] = None


class RetourClientResponse(BaseModel):
    id: int
    numero_retour: str
    client_id: int
    bon_sortie_id: Optional[int] = None
    date_retour: Optional[date] = None
    type_retour: Optional[str] = None
    motif: Optional[str] = None
    quantite: Optional[float] = None
    statut: str
    action: Optional[str] = None
    cout_traitement: Optional[float] = None
    notes: Optional[str] = None
    operateur: Optional[int] = None

    class Config:
        from_attributes = True


# LitigeTransporteur schemas — Batch 17 : alignés sur le modèle réel
# (date_litige → date_incident, statut/colonnes assureur et police reels).
class LitigeTransporteurCreate(BaseModel):
    transporteur_id: int
    mission_id: Optional[int] = None
    type_litige: str  # retard, avarie, perte, erreur_livraison
    description: str
    montant_reclame: Optional[float] = None
    assureur: Optional[str] = None
    numero_police: Optional[str] = None


class LitigeTransporteurUpdate(BaseModel):
    type_litige: Optional[str] = None
    description: Optional[str] = None
    montant_reclame: Optional[float] = None
    assureur: Optional[str] = None
    numero_police: Optional[str] = None


class LitigeTransporteurResolution(BaseModel):
    statut: str  # resolu | refuse | justice
    resolution: str
    montant_indemnise: Optional[float] = None  # maj montant_reclame si accord partiel


class LitigeTransporteurResponse(BaseModel):
    id: int
    numero_litige: str
    transporteur_id: int
    mission_id: Optional[int] = None
    date_incident: Optional[date] = None
    type_litige: Optional[str] = None
    description: Optional[str] = None
    montant_reclame: Optional[float] = None
    statut: str
    resolution: Optional[str] = None
    date_resolution: Optional[date] = None
    assureur: Optional[str] = None
    numero_police: Optional[str] = None

    class Config:
        from_attributes = True


# Colis schemas — Batch 19 : alignés sur le modèle réel (Colis porte
# numero_colis / emplacement / date_etiquetage(Date) / operateur ;
# reference_colis, code_barres, palette_id, date_creation, date_palettisation
# N'EXISTENT PAS — l'ancien ColisService y écrivait en silence ou levait
# TypeError). La palettisation n'étant pas modélisée (aucune colonne), elle
# est tracée dans `emplacement` (l'unique colonne de localisation réelle).
class ColisCreate(BaseModel):
    type_colis: Optional[str] = None  # carton, palette, caisse, sac
    poids: Optional[float] = None
    dimensions: Optional[str] = None  # format LxHxW
    volume: Optional[float] = None
    contenu: Optional[str] = None
    fragile: Optional[bool] = None
    empilable: Optional[bool] = None
    bon_sortie_id: Optional[int] = None


class ColisUpdate(BaseModel):
    type_colis: Optional[str] = None
    poids: Optional[float] = None
    dimensions: Optional[str] = None
    volume: Optional[float] = None
    contenu: Optional[str] = None
    fragile: Optional[bool] = None
    empilable: Optional[bool] = None
    emplacement: Optional[str] = None


class ColisResponse(BaseModel):
    id: int
    numero_colis: str
    bon_sortie_id: Optional[int] = None
    type_colis: Optional[str] = None
    poids: Optional[float] = None
    dimensions: Optional[str] = None
    volume: Optional[float] = None
    contenu: Optional[str] = None
    fragile: Optional[bool] = None
    empilable: Optional[bool] = None
    emplacement: Optional[str] = None
    date_etiquetage: Optional[date] = None  # colonne reelle de type Date
    operateur: Optional[int] = None

    class Config:
        from_attributes = True


# KPI Response schemas
class RotationStockResponse(BaseModel):
    # Batch 17 : expose les composantes reelles (sorties cumulees, stock
    # actuel) — rotation None quand le stock est a zero (indefinie, pas un 0
    # mensonger).
    article_id: int
    jours: int = 90
    sorties: float = 0.0
    stock_actuel: float = 0.0
    rotation: Optional[float] = None


class PrecisionInventaireResponse(BaseModel):
    # Batch 18 : precision None + message quand aucune ligne comptee — un
    # inventaire jamais mesure n'est pas un inventaire a 0 %.
    inventaire_id: int
    lignes_total: int = 0
    lignes_correctes: int = 0
    precision: Optional[float] = None
    message: Optional[str] = None


class PerformanceFournisseurResponse(BaseModel):
    # Batch 18 : note/taux/delai None quand la mesure est impossible
    # (aucune commande, aucune date de livraison mesurable) — plus de faux zero.
    fournisseur_id: int
    commandes: int = 0
    commandes_livrees: int = 0
    taux_livraison: Optional[float] = None
    delai_moyen_jours: Optional[float] = None
    note: Optional[float] = None
    message: Optional[str] = None


class ReapproLigneInfo(BaseModel):
    stock_id: int
    code_article: Optional[str] = None
    designation: Optional[str] = None
    quantite_commandee: float
    prix_unitaire: float
    prix_total: float


class ReapproIgnoreInfo(BaseModel):
    stock_id: int
    code_article: Optional[str] = None
    raison: str


class ReapproAutomatiqueResponse(BaseModel):
    # Batch 18 : une seule commande groupee (modele reel : lignes -> stock_id,
    # prix NOT NULL — les stocks sans prix sont IGNOREES et declarees, jamais
    # pricees a 0.0 invente).
    commande_id: int
    numero_commande: str
    lignes: List[ReapproLigneInfo]
    ignorees: List[ReapproIgnoreInfo]
