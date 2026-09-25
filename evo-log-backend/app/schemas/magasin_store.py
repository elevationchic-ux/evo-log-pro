"""
Magasin store-domain schemas (Tranche A) :
articles, clients, commandes, ordres de transfert, bandes de livraison.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CommandeStatut(str, Enum):
    BROUILLON = "brouillon"
    VALIDEE = "validee"
    EN_PREPARATION = "en_preparation"
    PRETE = "prete"
    LIVREE = "livree"
    ANNULEE = "annulee"


class TransfertStatut(str, Enum):
    BROUILLON = "brouillon"
    VALIDE = "valide"
    PAYE = "paye"
    EXPEDIE = "expedie"
    RECEPTIONNE = "receptionne"
    ANNULE = "annule"


# ─── Article ───────────────────────────────────────────────────────────────
class ArticleBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    designation: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    prix_unitaire: Optional[float] = None
    poids_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    code_barres: Optional[str] = None
    hs_code: Optional[str] = None
    is_active: bool = True


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    designation: Optional[str] = None
    description: Optional[str] = None
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    prix_unitaire: Optional[float] = None
    poids_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    code_barres: Optional[str] = None
    hs_code: Optional[str] = None
    is_active: Optional[bool] = None


class ArticleResponse(ArticleBase):
    id: int
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Client (proxy sur le modele Tiers/Client existant) ──────────────────────
class ClientBase(BaseModel):
    code: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    is_active: bool = True


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(BaseModel):
    id: int
    company_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


# ─── Commande ────────────────────────────────────────────────────────────────
class LigneCommandeBase(BaseModel):
    article_id: Optional[int] = None
    designation: Optional[str] = None
    quantite: float = 0
    prix_unitaire: Optional[float] = None
    montant: Optional[float] = None


class LigneCommandeCreate(LigneCommandeBase):
    pass


class LigneCommandeResponse(LigneCommandeBase):
    id: int

    class Config:
        from_attributes = True


class CommandeBase(BaseModel):
    client_id: Optional[int] = None
    type_commande: Optional[str] = "sortie"
    date_livraison_prevue: Optional[datetime] = None
    montant_total: Optional[float] = None
    devise: Optional[str] = "XAF"
    notes: Optional[str] = None


class CommandeCreate(CommandeBase):
    reference: Optional[str] = None
    lignes: List[LigneCommandeCreate] = []


class CommandeResponse(CommandeBase):
    id: int
    company_id: Optional[int] = None
    reference: str
    statut: CommandeStatut
    date_commande: Optional[datetime] = None
    lignes: List[LigneCommandeResponse] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Ordre de Transfert ──────────────────────────────────────────────────────
class OrdreTransfertBase(BaseModel):
    entrepot_source_id: Optional[int] = None
    entrepot_dest_id: Optional[int] = None
    article_id: Optional[int] = None
    quantite: float = 0
    motif: Optional[str] = None
    montant_paiement: Optional[float] = None


class OrdreTransfertCreate(OrdreTransfertBase):
    reference: Optional[str] = None


class OrdreTransfertResponse(OrdreTransfertBase):
    id: int
    company_id: Optional[int] = None
    reference: str
    statut: TransfertStatut
    date_transfert: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Bande de Livraison ──────────────────────────────────────────────────────
class BandeLivraisonBase(BaseModel):
    commande_id: Optional[int] = None
    ordre_transfert_id: Optional[int] = None
    client_id: Optional[int] = None
    statut: Optional[str] = "en_preparation"
    prepare_par: Optional[str] = None
    poids_total: Optional[float] = None
    nb_colis: Optional[int] = 0
    notes: Optional[str] = None


class BandeLivraisonCreate(BandeLivraisonBase):
    reference: Optional[str] = None


class BandeLivraisonUpdate(BaseModel):
    statut: Optional[str] = None
    prepare_par: Optional[str] = None
    poids_total: Optional[float] = None
    nb_colis: Optional[int] = None
    date_livraison: Optional[datetime] = None
    notes: Optional[str] = None


class BandeLivraisonResponse(BandeLivraisonBase):
    id: int
    company_id: Optional[int] = None
    reference: str
    date_preparation: Optional[datetime] = None
    date_livraison: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Enveloppe liste (spec "fix real + banner") ─────────────────────────────
class ListEnvelope(BaseModel):
    items: List[dict] = []
    total: int = 0
