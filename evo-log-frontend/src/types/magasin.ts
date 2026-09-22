/**
 * types/magasin.ts
 * Interfaces TypeScript synchronisées avec app/schemas/magasin.py (Pydantic)
 */

// ─── ENUMS ──────────────────────────────────────────────────────────────────

export enum UniteMesure {
  UDB = 'UDB',
  KG = 'KG',
  TONNE = 'TONNE',
  M3 = 'M3',
  M2 = 'M2',
  UNITE = 'UNITE'
}

export enum CategorieArticle {
  ALIMENTAIRE = "ALIMENTAIRE",
  PHARMACEUTIQUE = "PHARMACEUTIQUE",
  MATIERES_PREMIERES = "MATIERES_PREMIERES",
  PRODUITS_FINIS = "PRODUITS_FINIS",
  EMBALLAGES_PALETES = "EMBALLAGES_PALETES",
  EQUIPEMENT = "EQUIPEMENT",
  PIECES_DETACHEES = "PIECES_DETACHEES",
  MOBILIER_BUREAU_INFORMATIQUE = "MOBILIER_BUREAU_INFORMATIQUE",
  PRODUITS_DANGEREUX = "PRODUITS_DANGEREUX",
  PRODUITS_LUXE_VALEUR = "PRODUITS_LUXE_VALEUR",
  VRAC = "VRAC",
  HORS_GABARIT = "HORS_GABARIT"
}

export enum StatutStock {
  NORMAL = "NORMAL",
  DECHIRE = "DECHIRE",
  MOUILLE = "MOUILLE",
  ENDOMMAGE = "ENDOMMAGE",
  PERIME = "PERIME",
  EN_ATTENTE = "EN_ATTENTE",
  RESERVE = "RESERVE"
}

export enum StatutDeclaration {
  BROUILLON = "BROUILLON",
  SOUMISE = "SOUMISE",
  VALIDEE = "VALIDEE",
  REJETEE = "REJETEE",
  ANNULEE = "ANNULEE"
}

export enum StatutReception {
  EN_COURS = "EN_COURS",
  COMPLETEE = "COMPLETEE",
  ANNULEE = "ANNULEE"
}

export enum StatutCommande {
  BROUILLON = "BROUILLON",
  EN_COURS = "EN_COURS",
  EN_ATTENTE = "EN_ATTENTE",
  VERROUILLEE = "VERROUILLEE",
  PAYEE = "PAYEE",
  EN_PREPARATION = "EN_PREPARATION",
  PRETE = "PRETE",
  LIVREE = "LIVREE",
  ANNULEE = "ANNULEE"
}

export enum StatutFournisseur {
  ACTIF = "ACTIF",
  INACTIF = "INACTIF",
  BLOQUE = "BLOQUE"
}

export enum CategorieFournisseur {
  LOGISTIQUE = "LOGISTIQUE",
  IMPORT_EXPORT = "IMPORT_EXPORT",
  SERVICES = "SERVICES",
  MATERIEL = "MATERIEL"
}

// ─── MAGASIN ────────────────────────────────────────────────────────────────

export interface MagasinBase {
  code: string;
  nom: string;
  adresse?: string;
  ville?: string;
  pays: string;
  telephone?: string;
  email?: string;
  est_actif: boolean;
}

export interface MagasinCreate extends MagasinBase {}
export interface MagasinUpdate extends Partial<Omit<MagasinBase, 'code'>> {}

export interface Magasin extends MagasinBase {
  id: number;
  date_creation: string;
  date_modification?: string;
}

// ─── CLIENT MAGASIN ─────────────────────────────────────────────────────────

export interface ClientMagasinBase {
  code: string;
  nom: string;
  prenom?: string;
  raison_sociale?: string;
  telephone?: string;
  email?: string;
  adresse?: string;
  ville?: string;
  pays: string;
  numero_contribuable?: string;
  est_actif: boolean;
}

export interface ClientMagasinCreate extends ClientMagasinBase {}
export interface ClientMagasinUpdate extends Partial<ClientMagasinBase> {}

export interface ClientMagasin extends ClientMagasinBase {
  id: number;
  date_creation: string;
  date_modification?: string;
}

// ─── ARTICLE ────────────────────────────────────────────────────────────────

export interface ArticleBase {
  code_article: string;
  nom: string;
  description?: string;
  categorie?: CategorieArticle;
  unite_mesure: UniteMesure;
  poids_unitaire?: number;
  volume_unitaire?: number;
  est_actif: boolean;
}

export interface ArticleCreate extends ArticleBase {}
export interface ArticleUpdate extends Partial<Omit<ArticleBase, 'code_article'>> {}

export interface Article extends ArticleBase {
  id: number;
  date_creation: string;
  date_modification?: string;
}

// ─── DECLARATION ────────────────────────────────────────────────────────────

export interface LigneDeclarationBase {
  article_id: number;
  quantite_declaree: number;
  unite_mesure: UniteMesure;
  quantite_udb?: number;
}

export interface LigneDeclarationCreate extends LigneDeclarationBase {}
export interface LigneDeclaration extends LigneDeclarationBase {
  id: number;
  declaration_id: number;
  article?: Article;
}

export interface DeclarationBase {
  client_id: number;
  incoterm_id?: number;
  type_conteneur_id?: number;
  numero_conteneur?: string;
  date_arrivee_prevue?: string;
  statut: StatutDeclaration;
  notes?: string;
}

export interface DeclarationCreate extends DeclarationBase {
  lignes: LigneDeclarationCreate[];
}

export interface DeclarationUpdate extends Partial<Omit<DeclarationBase, 'client_id'>> {}

export interface Declaration extends DeclarationBase {
  id: number;
  numero_bl: string;
  date_declaration: string;
  cree_par?: string;
  date_creation: string;
  date_modification?: string;
  client?: ClientMagasin;
  lignes: LigneDeclaration[];
}

// ─── RECEPTION ──────────────────────────────────────────────────────────────

export interface LigneReceptionBase {
  article_id: number;
  quantite_recue: number;
  unite_mesure: UniteMesure;
  quantite_udb?: number;
}

export interface LigneReceptionCreate extends LigneReceptionBase {}
export interface LigneReception extends LigneReceptionBase {
  id: number;
  reception_id: number;
  article?: Article;
}

export interface ReceptionBase {
  declaration_id: number;
  magasin_id: number;
  statut: StatutReception;
  notes?: string;
}

export interface ReceptionCreate extends ReceptionBase {
  lignes: LigneReceptionCreate[];
}

export interface ReceptionUpdate extends Partial<Omit<ReceptionBase, 'declaration_id' | 'magasin_id'>> {}

export interface Reception extends ReceptionBase {
  id: number;
  numero_reception: string;
  date_reception: string;
  recu_par?: string;
  date_creation: string;
  date_modification?: string;
  declaration?: Declaration;
  magasin?: Magasin;
  lignes: LigneReception[];
}

// ─── STOCK ──────────────────────────────────────────────────────────────────

export interface StockBase {
  magasin_id: number;
  article_id: number;
  quantite_disponible: number;
  quantite_udb: number;
  statut: StatutStock;
}

export interface StockCreate extends StockBase {}
export interface StockUpdate extends Partial<StockBase> {}

export interface Stock extends StockBase {
  id: number;
  derniere_maj?: string;
  date_creation: string;
  magasin?: Magasin;
  article?: Article;
}

export interface StockFilter {
  code_article?: string;
  magasin_ids?: number[];
  client_id?: number;
  date_debut?: string;
  date_fin?: string;
  statut?: StatutStock;
  categorie?: CategorieArticle;
}

// ─── COMMANDE ───────────────────────────────────────────────────────────────

export interface LigneCommandeBase {
  article_id: number;
  quantite_demandee: number;
  quantite_livree: number;
  unite_mesure: UniteMesure;
  prix_unitaire?: number;
}

export interface LigneCommandeCreate extends LigneCommandeBase {}
export interface LigneCommande extends LigneCommandeBase {
  id: number;
  commande_id: number;
  article?: Article;
}

export interface CommandeBase {
  client_id: number;
  date_livraison_souhaitee?: string;
  statut: StatutCommande;
  est_verrouille: boolean;
  paiement_valide: boolean;
  notes?: string;
}

export interface CommandeCreate extends CommandeBase {
  numero_commande: string;
  date_commande: string;
  lignes: LigneCommandeCreate[];
}

export interface CommandeUpdate extends Partial<Omit<CommandeBase, 'client_id'>> {}

export interface Commande extends CommandeBase {
  id: number;
  numero_commande: string;
  date_commande: string;
  valide_par?: string;
  date_validation?: string;
  cree_par?: string;
  date_creation: string;
  date_modification?: string;
  client?: ClientMagasin;
  lignes: LigneCommande[];
}

// ─── BANDE LIVRAISON ────────────────────────────────────────────────────────

export interface LigneBandeLivraisonBase {
  article_id: number;
  quantite: number;
  unite_mesure: UniteMesure;
}

export interface LigneBandeLivraisonCreate extends LigneBandeLivraisonBase {}
export interface LigneBandeLivraison extends LigneBandeLivraisonBase {
  id: number;
  bande_id: number;
}

export interface BandeLivraisonBase {
  commande_id: number;
  magasin_id: number;
  date_livraison?: string;
  statut: string;
  nombre_camions: number;
  notes?: string;
}

export interface BandeLivraisonCreate extends BandeLivraisonBase {
  lignes: LigneBandeLivraisonCreate[];
}

export interface BandeLivraisonUpdate extends Partial<Omit<BandeLivraisonBase, 'commande_id' | 'magasin_id'>> {}

export interface BandeLivraison extends BandeLivraisonBase {
  id: number;
  numero_bande: string;
  date_creation: string;
  prepare_par?: string;
  commande?: Commande;
  magasin?: Magasin;
  lignes_bande: LigneBandeLivraison[];
}

// ─── FOURNISSEUR (SUPPLIER) ────────────────────────────────────────────────

export interface SupplierBase {
  code_fournisseur: string;
  raison_sociale: string;
  acronyme?: string;
  type_entite?: string;
  niu: string;
  rccm?: string;
  adresse?: string;
  boite_postale?: string;
  ville?: string;
  region?: string;
  telephone?: string;
  email?: string;
  conditions_paiement?: string;
  devise?: string;
  limite_credit?: number;
  id_fiscal?: string;
  compte_bancaire?: string;
  nom_banque?: string;
  statut: StatutFournisseur;
  est_actif: boolean;
}

export interface SupplierCreate extends Omit<SupplierBase, 'statut' | 'est_actif'> {
  statut?: StatutFournisseur;
  est_actif?: boolean;
}

export interface SupplierUpdate extends Partial<SupplierCreate> {}

export interface Supplier extends SupplierBase {
  id: number;
  cree_par?: string;
  date_creation: string;
  date_modification?: string;
}

export interface SupplierProfile {
  id: number;
  supplier_id: number;
  categorie_fournisseur?: CategorieFournisseur;
  delai_moyen_livraison?: number;
  qualite_service?: string;
  notes?: string;
  date_evaluation?: string;
}

// ─── MASTER DATA / REFERENCES ───────────────────────────────────────────────

export interface IncotermBase {
  code: string;
  nom: string;
  description?: string;
  est_actif: boolean;
}

export interface IncotermCreate extends IncotermBase {}
export interface IncotermUpdate extends Partial<IncotermBase> {}
export interface Incoterm extends IncotermBase {
  id: number;
  date_creation: string;
}

export interface TypeConteneurBase {
  code: string;
  nom: string;
  description?: string;
  longueur?: string;
  type_conteneur?: string;
  est_actif: boolean;
}

export interface TypeConteneurCreate extends TypeConteneurBase {}
export interface TypeConteneurUpdate extends Partial<TypeConteneurBase> {}
export interface TypeConteneur extends TypeConteneurBase {
  id: number;
  date_creation: string;
}

// ─── TRACABILITE ────────────────────────────────────────────────────────────

export interface TransactionBase {
  code_transaction: string;
  nom: string;
  description?: string;
  interface: string;
  role_requis?: string;
  est_actif: boolean;
}

export interface Transaction extends TransactionBase {
  id: number;
  date_creation: string;
  date_modification?: string;
}

export interface OperationTrace {
  id: number;
  numero_ot: string;
  type_operation: string;
  table_cible: string;
  enregistrement_id: number;
  utilisateur_id?: number;
  donnees_operation?: string;
  date_operation: string;
  est_annule: boolean;
  date_annulation?: string;
  annule_par?: string;
}

// API Service for Magasin Module

export interface StockItem {
  id: number;
  code: string;
  description: string;
  quantity: number;
  unit: string;
  location: string;
  category: string;
  minStock: number;
  maxStock: number;
}

export interface StockMovement {
  id: number;
  itemId: string;
  type: 'in' | 'out' | 'transfer';
  quantity: number;
  date: string;
  reason: string;
  userId: string;
}

export interface Reception {
  id: number;
  reference: string;
  supplier: string;
  date: string;
  status: 'pending' | 'received' | 'validated';
  items: Array<{ itemId: string; quantity: number; unitPrice: number }>;
}

export interface RemovalSlip {
  id: number;
  numero_bon: string;
  magasin_source: string;
  magasin_destination: string;
  article_id: string;
  quantite: number;
  unite: string;
  declaration_douaniere: string;
  motif: string;
  observations: string;
  statut: string;
  autorise_par: string;
  date_autorisation: string;
  date_bon: string;
  cree_par: string;
  date_creation: string;
  date_modification: string;
}

export interface ReceptionMag3 {
  id: number;
  numero_reception: string;
  removal_slip_id: string;
  magasin_source: string;
  magasin_destination: string;
  article_id: string;
  quantite_attendue: number;
  quantite_recue: number;
  unite: string;
  declaration_douaniere: string;
  recu_par: string;
  date_reception: string;
  observations: string;
  statut: string;
  cree_par: string;
  date_creation: string;
  date_modification: string;
}

