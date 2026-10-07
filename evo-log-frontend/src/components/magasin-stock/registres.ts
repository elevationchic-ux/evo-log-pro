/**
 * Configs Registre pour magasin-stock (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("magasin-stock");

function col(name: string, label: string, labelEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {
  return { name, label, labelEn, ...opts } as ColonneRegistre;
}

function txt(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { name, label, labelEn, type: "texte", ...opts } as ChampRegistre;
}

function num(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { name, label, labelEn, type: "nombre", ...opts } as ChampRegistre;
}

function dt(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "date" } as ChampRegistre;
}

function dtx(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "date" } as ChampRegistre;
}

function area(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "zone" } as ChampRegistre;
}

function chk(name: string, label: string, labelEn: string): ChampRegistre {
  return { name, label, labelEn, type: "booleen" } as ChampRegistre;
}

function sel(name: string, label: string, labelEn: string, nomKey: string): ChampRegistre {
  return { name, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;
}

function filtreSel(name: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {
  return { name, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;
}

export const registreArticleCatalog: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "article_catalog",
  tcode: "registre-article-catalog",
  icon: Icons.Boxes,
  titre: "Referentiel articles / SKU",
  titreEn: "Article catalog / SKU",
  description: "Catalogue articles avec dimensions et unites.",
  descriptionEn: "Article catalog with dimensions and units.",
  aide: "Chaque SKU doit pointer vers une categorie valide.",
  aideEn: "Every SKU must reference a valid category.",
  lister: (params) => api.lister("article-catalogs", params),
  creer: (data) => api.creer("article-catalogs", data),
  modifier: (id, data) => api.modifier("article-catalogs", id, data),
  unicite: "code_sku",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_sku", "Code SKU", "SKU code"),
    col("designation", "Designation", "Name"),
    col("categorie", "Categorie", "Category"),
    col("unite_principale", "Unite", "UoM"),
    col("code_barre", "Code barre", "Barcode"),
    col("poids_unitaire_kg", "Poids unitaire (kg)", "Unit weight (kg)"),
    col("volume_m3", "Volume (m3)", "Volume (m3)"),
    col("prix_achat_moyen_xaf", "PA moyen", "Avg purchase price"),
    col("prix_vente_xaf", "Prix vente", "Sale price"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_sku", "Code SKU", "SKU code", { requisCreation: true }),
    txt("designation", "Designation", "Name"),
    txt("categorie", "Categorie", "Category"),
    txt("unite_principale", "Unite", "UoM"),
    txt("code_barre", "Code barre", "Barcode"),
    num("poids_unitaire_kg", "Poids unitaire (kg)", "Unit weight (kg)"),
    num("volume_m3", "Volume (m3)", "Volume (m3)"),
    num("prix_achat_moyen_xaf", "PA moyen", "Avg purchase price"),
    num("prix_vente_xaf", "Prix vente", "Sale price"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSupplierArticle: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "supplier_catalog",
  tcode: "registre-supplier-catalog",
  icon: Icons.Users,
  titre: "Fournisseurs par article",
  titreEn: "Suppliers per article",
  description: "Matrice fournisseurs / prix / delais.",
  descriptionEn: "Supplier / price / lead time matrix.",
  aide: "Au moins 2 fournisseurs references par article critique.",
  aideEn: "At least 2 suppliers per critical article.",
  lister: (params) => api.lister("supplier-articles", params),
  creer: (data) => api.creer("supplier-articles", data),
  modifier: (id, data) => api.modifier("supplier-articles", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("article_id", "Article", "Article"),
    col("fournisseur_id", "Fournisseur", "Supplier"),
    col("prix_unitaire_xaf", "Prix unitaire XAF", "Unit price XAF"),
    col("delai_livraison_jours", "Delai (j)", "Lead time (d)"),
    col("quantite_min_commande", "Qte min", "MOQ"),
    col("devise", "Devise", "Currency"),
    col("conditions_paiement", "Conditions paiement", "Payment terms"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("article_id", "Article", "Article"),
    num("fournisseur_id", "Fournisseur", "Supplier"),
    num("prix_unitaire_xaf", "Prix unitaire XAF", "Unit price XAF"),
    num("delai_livraison_jours", "Delai (j)", "Lead time (d)"),
    num("quantite_min_commande", "Qte min", "MOQ"),
    txt("devise", "Devise", "Currency"),
    txt("conditions_paiement", "Conditions paiement", "Payment terms"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registrePurchaseOrderDeep: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "purchase_order",
  tcode: "registre-purchase-orders",
  icon: Icons.ShoppingCart,
  titre: "Commandes d'achat",
  titreEn: "Purchase orders",
  description: "Bons de commande acheteur avec lignes.",
  descriptionEn: "Buyer purchase orders with lines.",
  aide: "La reception genere le bon d'entree automatiquement.",
  aideEn: "Receipt generates goods-in automatically.",
  lister: (params) => api.lister("purchase-orders", params),
  creer: (data) => api.creer("purchase-orders", data),
  modifier: (id, data) => api.modifier("purchase-orders", id, data),
  unicite: "numero_commande",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_commande", "Numero", "Number"),
    col("fournisseur_id", "Fournisseur", "Supplier"),
    col("date_commande", "Date", "Date"),
    col("date_livraison_prevue", "Livraison prevue", "Planned delivery"),
    col("montant_total_xaf", "Montant XAF", "Amount XAF"),
    col("nb_lignes", "Nb lignes", "Lines"),
    col("acheteur", "Acheteur", "Buyer"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_commande", "Numero", "Number", { requisCreation: true }),
    num("fournisseur_id", "Fournisseur", "Supplier"),
    dt("date_commande", "Date", "Date"),
    dt("date_livraison_prevue", "Livraison prevue", "Planned delivery"),
    num("montant_total_xaf", "Montant XAF", "Amount XAF"),
    num("nb_lignes", "Nb lignes", "Lines"),
    txt("acheteur", "Acheteur", "Buyer"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreQualityInspection: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "quality_control",
  tcode: "registre-quality-control",
  icon: Icons.ClipboardCheck,
  titre: "Controle qualite a reception",
  titreEn: "Receiving quality control",
  description: "Inspection quantitative et qualitative a reception.",
  descriptionEn: "Quantitative and qualitative receiving inspection.",
  aide: "Toute non-conformite declenche une fiche 8D.",
  aideEn: "Any non-conformity triggers an 8D sheet.",
  lister: (params) => api.lister("quality-inspections", params),
  creer: (data) => api.creer("quality-inspections", data),
  modifier: (id, data) => api.modifier("quality-inspections", id, data),
  unicite: "numero_controle",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_controle", "Numero", "Number"),
    col("reception_id", "Reception", "Receipt"),
    col("article_id", "Article", "Article"),
    col("quantite_inspekte", "Qte inspekte", "Inspected quantity"),
    col("quantite_conforme", "Qte conforme", "Conforming quantity"),
    col("quantite_rebutee", "Qte rebutee", "Rejected quantity"),
    col("resultat", "Resultat", "Result"),
    col("inspecteur", "Inspecteur", "Inspector"),
    col("date_controle", "Date", "Date"),
    col("observations", "Observations", "Observations"),
  ],
  champs: [
    txt("numero_controle", "Numero", "Number", { requisCreation: true }),
    num("reception_id", "Reception", "Receipt"),
    num("article_id", "Article", "Article"),
    num("quantite_inspekte", "Qte inspekte", "Inspected quantity"),
    num("quantite_conforme", "Qte conforme", "Conforming quantity"),
    num("quantite_rebutee", "Qte rebutee", "Rejected quantity"),
    sel("resultat", "Resultat", "Result", "resultat"),
    txt("inspecteur", "Inspecteur", "Inspector"),
    dt("date_controle", "Date", "Date"),
    txt("observations", "Observations", "Observations"),
  ],
};


export const registreStockAlert: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "stock_alert",
  tcode: "registre-stock-alerts",
  icon: Icons.Bell,
  titre: "Seuils et alertes rupture",
  titreEn: "Thresholds and shortage alerts",
  description: "Seuil mini, max, point de commande.",
  descriptionEn: "Min, max, reorder point.",
  aide: "Le systeme declenche une requisition automatique.",
  aideEn: "System triggers an automatic requisition.",
  lister: (params) => api.lister("stock-alerts", params),
  creer: (data) => api.creer("stock-alerts", data),
  modifier: (id, data) => api.modifier("stock-alerts", id, data),
  unicite: "code_alerte",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_alerte", "Code alerte", "Alert code"),
    col("article_id", "Article", "Article"),
    col("depot_id", "Depot", "Warehouse"),
    col("seuil_min", "Seuil mini", "Min threshold"),
    col("seuil_max", "Seuil maxi", "Max threshold"),
    col("point_commande", "Point de commande", "Reorder point"),
    col("quantite_actuelle", "Qte actuelle", "Current qty"),
    col("derniere_alerte", "Derniere alerte", "Last alert"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_alerte", "Code alerte", "Alert code", { requisCreation: true }),
    num("article_id", "Article", "Article"),
    num("depot_id", "Depot", "Warehouse"),
    num("seuil_min", "Seuil mini", "Min threshold"),
    num("seuil_max", "Seuil maxi", "Max threshold"),
    num("point_commande", "Point de commande", "Reorder point"),
    num("quantite_actuelle", "Qte actuelle", "Current qty"),
    dtx("derniere_alerte", "Derniere alerte", "Last alert"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreExpiryRecord: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "expiry_tracking",
  tcode: "registre-expiry-tracking",
  icon: Icons.Calendar,
  titre: "Peremption / FEFO",
  titreEn: "Expiry / FEFO",
  description: "Lots dates de peremption par article.",
  descriptionEn: "Lot expiry dates per article.",
  aide: "Priorite FEFO : premier perime, premier sorti.",
  aideEn: "FEFO priority: first expired, first shipped.",
  lister: (params) => api.lister("expiry-records", params),
  creer: (data) => api.creer("expiry-records", data),
  modifier: (id, data) => api.modifier("expiry-records", id, data),
  unicite: "numero_lot",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_lot", "Numero lot", "Lot number"),
    col("article_id", "Article", "Article"),
    col("quantite", "Quantite", "Quantity"),
    col("date_peremption", "Date peremption", "Expiry date"),
    col("date_reception", "Date reception", "Reception date"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_lot", "Numero lot", "Lot number", { requisCreation: true }),
    num("article_id", "Article", "Article"),
    num("quantite", "Quantite", "Quantity"),
    dt("date_peremption", "Date peremption", "Expiry date"),
    dt("date_reception", "Date reception", "Reception date"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreSerialNumber: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "serial_tracking",
  tcode: "registre-serial-tracking",
  icon: Icons.Fingerprint,
  titre: "Tracabilite numeros serie",
  titreEn: "Serial number tracking",
  description: "Numeros serie / IMEI rattaches a une sortie.",
  descriptionEn: "Serial / IMEI numbers attached to an outbound.",
  aide: "Obligatoire pour materiel informatique.",
  aideEn: "Mandatory for IT equipment.",
  lister: (params) => api.lister("serial-numbers", params),
  creer: (data) => api.creer("serial-numbers", data),
  modifier: (id, data) => api.modifier("serial-numbers", id, data),
  unicite: "numero_serial",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_serial", "Numero serie", "Serial"),
    col("article_id", "Article", "Article"),
    col("numero_lot", "Numero lot", "Lot"),
    col("statut", "Statut", "Status"),
    col("date_entree", "Date entree", "Entry date"),
    col("date_sortie", "Date sortie", "Exit date"),
    col("destination", "Destination", "Destination"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_serial", "Numero serie", "Serial", { requisCreation: true }),
    num("article_id", "Article", "Article"),
    txt("numero_lot", "Numero lot", "Lot"),
    sel("statut", "Statut", "Status", "statut"),
    dt("date_entree", "Date entree", "Entry date"),
    dt("date_sortie", "Date sortie", "Exit date"),
    txt("destination", "Destination", "Destination"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registrePackingUnit: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "packing_unit",
  tcode: "registre-packing-units",
  icon: Icons.Package,
  titre: "Unites de conditionnement",
  titreEn: "Packaging units",
  description: "Colis, cartons, palettes, conteneurs.",
  descriptionEn: "Parcels, cartons, pallets, containers.",
  aide: "Chaque UC rattachee a une tare.",
  aideEn: "Each PU has a tare weight.",
  lister: (params) => api.lister("packing-units", params),
  creer: (data) => api.creer("packing-units", data),
  modifier: (id, data) => api.modifier("packing-units", id, data),
  unicite: "code_uc",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_uc", "Code UC", "PU code"),
    col("type_uc", "Type UC", "Type"),
    col("dimensions", "Dimensions", "Dimensions"),
    col("poids_tare_kg", "Poids tare (kg)", "Tare (kg)"),
    col("capacite_max_kg", "Capacite (kg)", "Capacity (kg)"),
    col("nb_unites_principales", "Nb unites", "Units count"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("code_uc", "Code UC", "PU code", { requisCreation: true }),
    sel("type_uc", "Type UC", "Type", "type_uc"),
    txt("dimensions", "Dimensions", "Dimensions"),
    num("poids_tare_kg", "Poids tare (kg)", "Tare (kg)"),
    num("capacite_max_kg", "Capacite (kg)", "Capacity (kg)"),
    num("nb_unites_principales", "Nb unites", "Units count"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registreStockReturn: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "returns_management",
  tcode: "registre-returns-management",
  icon: Icons.Undo2,
  titre: "Retours et avoirs stock",
  titreEn: "Returns and credit notes",
  description: "Retours clients / fournisseurs avec motif.",
  descriptionEn: "Client / supplier returns with reason.",
  aide: "Avoir genere seulement apres validation controle qualite.",
  aideEn: "Credit issued after quality control validation.",
  lister: (params) => api.lister("stock-returns", params),
  creer: (data) => api.creer("stock-returns", data),
  modifier: (id, data) => api.modifier("stock-returns", id, data),
  unicite: "numero_retour",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_retour", "Numero retour", "Return number"),
    col("type_retour", "Type", "Type"),
    col("client_id", "Client", "Client"),
    col("fournisseur_id", "Fournisseur", "Supplier"),
    col("date_retour", "Date", "Date"),
    col("article_id", "Article", "Article"),
    col("quantite", "Quantite", "Quantity"),
    col("motif", "Motif", "Reason"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_retour", "Numero retour", "Return number", { requisCreation: true }),
    sel("type_retour", "Type", "Type", "type_retour"),
    num("client_id", "Client", "Client"),
    num("fournisseur_id", "Fournisseur", "Supplier"),
    dt("date_retour", "Date", "Date"),
    num("article_id", "Article", "Article"),
    num("quantite", "Quantite", "Quantity"),
    txt("motif", "Motif", "Reason"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreConsignmentStock: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "consignment_stock",
  tcode: "registre-consignment-stock",
  icon: Icons.HandCoins,
  titre: "Stock en consignation",
  titreEn: "Consignment stock",
  description: "Stock detenu pour un tiers.",
  descriptionEn: "Stock held on behalf of a third party.",
  aide: "Facturation au retrait reel, pas au depot.",
  aideEn: "Billing on actual withdrawal, not on deposit.",
  lister: (params) => api.lister("consignment-stocks", params),
  creer: (data) => api.creer("consignment-stocks", data),
  modifier: (id, data) => api.modifier("consignment-stocks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("proprietaire_id", "Proprietaire", "Owner"),
    col("article_id", "Article", "Article"),
    col("quantite_deposee", "Qte deposee", "Deposited quantity"),
    col("quantite_retiree", "Qte retiree", "Withdrawn quantity"),
    col("date_depot", "Date depot", "Deposit date"),
    col("date_limite", "Date limite", "Deadline"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("proprietaire_id", "Proprietaire", "Owner"),
    num("article_id", "Article", "Article"),
    num("quantite_deposee", "Qte deposee", "Deposited quantity"),
    num("quantite_retiree", "Qte retiree", "Withdrawn quantity"),
    dt("date_depot", "Date depot", "Deposit date"),
    dt("date_limite", "Date limite", "Deadline"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreStockValuation: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "stock_valuation",
  tcode: "registre-stock-valuation",
  icon: Icons.Calculator,
  titre: "Valorisation du stock",
  titreEn: "Stock valuation",
  description: "Calcul CMUP / COI par article et periode.",
  descriptionEn: "Avg cost / FIFO by article and period.",
  aide: "Methode figee pour l'exercice.",
  aideEn: "Method frozen for the fiscal year.",
  lister: (params) => api.lister("stock-valuations", params),
  creer: (data) => api.creer("stock-valuations", data),
  modifier: (id, data) => api.modifier("stock-valuations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("periode", "Periode", "Period"),
    col("article_id", "Article", "Article"),
    col("methode", "Methode", "Method"),
    col("quantite_fin", "Qte fin", "Ending quantity"),
    col("valeur_cmup_xaf", "Valeur CMUP", "Avg cost value"),
    col("valeur_coi_xaf", "Valeur COI", "FIFO value"),
    col("date_calcul", "Date calcul", "Calculation date"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("periode", "Periode", "Period"),
    num("article_id", "Article", "Article"),
    sel("methode", "Methode", "Method", "methode"),
    num("quantite_fin", "Qte fin", "Ending quantity"),
    num("valeur_cmup_xaf", "Valeur CMUP", "Avg cost value"),
    num("valeur_coi_xaf", "Valeur COI", "FIFO value"),
    dt("date_calcul", "Date calcul", "Calculation date"),
  ],
};


export const registreWmsKpi: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "wms_analytics",
  tcode: "registre-wms-analytics",
  icon: Icons.BarChart3,
  titre: "KPIs magasin",
  titreEn: "Warehouse KPIs",
  description: "Rotation, rupture, taux de service, cadence de preparation.",
  descriptionEn: "Turnover, shortage, service rate, picking.",
  aide: "Revu mensuellement avec le chef magasinier.",
  aideEn: "Reviewed monthly with the warehouse lead.",
  lister: (params) => api.lister("wms-kpis", params),
  creer: (data) => api.creer("wms-kpis", data),
  modifier: (id, data) => api.modifier("wms-kpis", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("periode_debut", "Debut", "Start"),
    col("periode_fin", "Fin", "End"),
    col("rotation", "Rotation", "Turnover"),
    col("rupture_pct", "Rupture %", "Shortage %"),
    col("taux_service_pct", "Taux service %", "Service %"),
    col("cadence_choix_lignes_h", "Cadence lignes/h", "Pick lines/h"),
    col("ecart_inventaire_pct", "Ecart inventaire %", "Inventory gap %"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    dt("periode_debut", "Debut", "Start"),
    dt("periode_fin", "Fin", "End"),
    num("rotation", "Rotation", "Turnover"),
    num("rupture_pct", "Rupture %", "Shortage %"),
    num("taux_service_pct", "Taux service %", "Service %"),
    num("cadence_choix_lignes_h", "Cadence lignes/h", "Pick lines/h"),
    num("ecart_inventaire_pct", "Ecart inventaire %", "Inventory gap %"),
    txt("notes", "Notes", "Notes"),
  ],
};

