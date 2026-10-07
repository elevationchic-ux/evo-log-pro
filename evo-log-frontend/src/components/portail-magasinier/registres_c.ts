/**
 * Configs Registre pour portail-magasinier (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-magasinier");

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

export const registreMagcPickingTask: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "picking_task",
  tcode: "registre-picking-tasks",
  icon: Icons.ListChecks,
  titre: "Taches de preparation",
  titreEn: "Picking tasks",
  description: "Ordre de prelevement par emplacement.",
  descriptionEn: "Pick order per location.",
  aide: "La quantite prelevee doit egaler la quantite demandee.",
  aideEn: "Picked quantity must equal requested.",
  lister: (params) => api.lister("magc-picking-tasks", params),
  creer: (data) => api.creer("magc-picking-tasks", data),
  modifier: (id, data) => api.modifier("magc-picking-tasks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ordre", "Ordre", "Order"),
    col("emplacement", "Emplacement", "Location"),
    col("quantite", "Quantite", "Quantity"),
    col("prepareur", "Preparateur", "Picker"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ordre", "Ordre", "Order"),
    txt("emplacement", "Emplacement", "Location"),
    num("quantite", "Quantite", "Quantity"),
    txt("prepareur", "Preparateur", "Picker"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcPackingSlip: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "packing_slip",
  tcode: "registre-packing-slips",
  icon: Icons.Box,
  titre: "Bons de colisage",
  titreEn: "Packing slips",
  description: "Consigne du contenu des colis d' une commande.",
  descriptionEn: "Record of the parcel contents of an order.",
  aide: "Nb colis et poids engagent l' expedition.",
  aideEn: "Parcel count and weight commit the shipment.",
  lister: (params) => api.lister("magc-packing-slips", params),
  creer: (data) => api.creer("magc-packing-slips", data),
  modifier: (id, data) => api.modifier("magc-packing-slips", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("commande", "Commande", "Order"),
    col("nb_colis", "Nombre de colis", "Parcel count"),
    col("poids", "Poids", "Weight"),
    col("operateur", "Operateur", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("commande", "Commande", "Order"),
    num("nb_colis", "Nombre de colis", "Parcel count"),
    num("poids", "Poids", "Weight"),
    txt("operateur", "Operateur", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcPutawayTask: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "putaway_task",
  tcode: "registre-put-away-tasks",
  icon: Icons.Archive,
  titre: "Taches de mise en place",
  titreEn: "Put-away tasks",
  description: "Rangement de la marchandise recue vers son emplacement.",
  descriptionEn: "Moving received goods to their location.",
  aide: "De (reception) vers (emplacement) trace le mouvement.",
  aideEn: "From (receiving) to (location) traces the move.",
  lister: (params) => api.lister("magc-put-away-tasks", params),
  creer: (data) => api.creer("magc-put-away-tasks", data),
  modifier: (id, data) => api.modifier("magc-put-away-tasks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("article", "Article", "Item"),
    col("quantite", "Quantite", "Quantity"),
    col("de", "Depuis", "From"),
    col("vers", "Vers", "To"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("article", "Article", "Item"),
    num("quantite", "Quantite", "Quantity"),
    txt("de", "Depuis", "From"),
    txt("vers", "Vers", "To"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcCycleCount: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "cycle_count",
  tcode: "registre-cycle-counts",
  icon: Icons.ClipboardList,
  titre: "Inventaires tournants",
  titreEn: "Cycle counts",
  description: "Comptage ponctuel par emplacement.",
  descriptionEn: "Spot count per location.",
  aide: "L' ecart physique - theorique est mesure.",
  aideEn: "Physical minus theoretical variance is measured.",
  lister: (params) => api.lister("magc-cycle-counts", params),
  creer: (data) => api.creer("magc-cycle-counts", data),
  modifier: (id, data) => api.modifier("magc-cycle-counts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("emplacement", "Emplacement", "Location"),
    col("theorique", "Quantite theorique", "Theoretical qty"),
    col("physique", "Quantite physique", "Physical qty"),
    col("compteur", "Compteur", "Counter"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("emplacement", "Emplacement", "Location"),
    num("theorique", "Quantite theorique", "Theoretical qty"),
    num("physique", "Quantite physique", "Physical qty"),
    txt("compteur", "Compteur", "Counter"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcInternalMove: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "internal_move",
  tcode: "registre-internal-moves",
  icon: Icons.MoveRight,
  titre: "Transferts internes",
  titreEn: "Internal moves",
  description: "Deplacement d' une quantite entre deux emplacements.",
  descriptionEn: "Movement of a quantity between two locations.",
  aide: "Origine et destination attestent le chemin.",
  aideEn: "Origin and destination evidence the path.",
  lister: (params) => api.lister("magc-internal-moves", params),
  creer: (data) => api.creer("magc-internal-moves", data),
  modifier: (id, data) => api.modifier("magc-internal-moves", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("article", "Article", "Item"),
    col("quantite", "Quantite", "Quantity"),
    col("origine", "Origine", "Origin"),
    col("destination", "Destination", "Destination"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("article", "Article", "Item"),
    num("quantite", "Quantite", "Quantity"),
    txt("origine", "Origine", "Origin"),
    txt("destination", "Destination", "Destination"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcGoodsIssue: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "goods_issue",
  tcode: "registre-goods-issues",
  icon: Icons.Send,
  titre: "Sorties de magasin",
  titreEn: "Goods issues",
  description: "Sortie de matiere sur demande interne.",
  descriptionEn: "Material issue on internal demand.",
  aide: "Le beneficiaire justifie la sortie.",
  aideEn: "The requester justifies the issue.",
  lister: (params) => api.lister("magc-goods-issues", params),
  creer: (data) => api.creer("magc-goods-issues", data),
  modifier: (id, data) => api.modifier("magc-goods-issues", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("demande", "Demande", "Request"),
    col("article", "Article", "Item"),
    col("quantite", "Quantite", "Quantity"),
    col("beneficiaire", "Beneficiaire", "Requester"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("demande", "Demande", "Request"),
    txt("article", "Article", "Item"),
    num("quantite", "Quantite", "Quantity"),
    txt("beneficiaire", "Beneficiaire", "Requester"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcReturnProcessing: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "return_processing",
  tcode: "registre-returns-processing",
  icon: Icons.Undo2,
  titre: "Traitement des retours",
  titreEn: "Returns processing",
  description: "Reception et tri des retours clients/fournisseurs.",
  descriptionEn: "Receipt and sorting of client/supplier returns.",
  aide: "Le motif conditionne la destination (repro, destruction).",
  aideEn: "The reason routes it (reput away, scrap).",
  lister: (params) => api.lister("magc-returns-processing", params),
  creer: (data) => api.creer("magc-returns-processing", data),
  modifier: (id, data) => api.modifier("magc-returns-processing", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("retour", "Type de retour", "Return type"),
    col("article", "Article", "Item"),
    col("quantite", "Quantite", "Quantity"),
    col("motif", "Motif", "Reason"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("retour", "Type de retour", "Return type"),
    txt("article", "Article", "Item"),
    num("quantite", "Quantite", "Quantity"),
    txt("motif", "Motif", "Reason"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcLabelPrint: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "label_print",
  tcode: "registre-label-printing",
  icon: Icons.Tags,
  titre: "Edition d' etiquettes",
  titreEn: "Label printing",
  description: "Impression d' etiquettes articles/palettes.",
  descriptionEn: "Printing of item/pallet labels.",
  aide: "Le type d' etiquette conditionne le contenu imprime.",
  aideEn: "Label type drives printed content.",
  lister: (params) => api.lister("magc-label-printing", params),
  creer: (data) => api.creer("magc-label-printing", data),
  modifier: (id, data) => api.modifier("magc-label-printing", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("article", "Article", "Item"),
    col("nombre", "Nombre", "Count"),
    col("type_etiquette", "Type d' etiquette", "Label type"),
    col("operateur", "Operateur", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("article", "Article", "Item"),
    num("nombre", "Nombre", "Count"),
    txt("type_etiquette", "Type d' etiquette", "Label type"),
    txt("operateur", "Operateur", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcPalletBuild: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "pallet_build",
  tcode: "registre-pallet-building",
  icon: Icons.Layers,
  titre: "Constitution de palettes",
  titreEn: "Pallet building",
  description: "Gerlement des cartons sur palette.",
  descriptionEn: "Casting cartons onto a pallet.",
  aide: "Hauteur et poids total conditionnent la manutention.",
  aideEn: "Height and total weight gate handling.",
  lister: (params) => api.lister("magc-pallet-building", params),
  creer: (data) => api.creer("magc-pallet-building", data),
  modifier: (id, data) => api.modifier("magc-pallet-building", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("commande", "Commande", "Order"),
    col("nb_cartons", "Nombre de cartons", "Carton count"),
    col("hauteur_cm", "Hauteur (cm)", "Height (cm)"),
    col("poids_total", "Poids total", "Total weight"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("commande", "Commande", "Order"),
    num("nb_cartons", "Nombre de cartons", "Carton count"),
    num("hauteur_cm", "Hauteur (cm)", "Height (cm)"),
    num("poids_total", "Poids total", "Total weight"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcEquipmentCheck: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "equipment_check",
  tcode: "registre-equipment-checks",
  icon: Icons.Wrench,
  titre: "Controles engins",
  titreEn: "Equipment checks",
  description: "Verification quotidienne du materiel de manutention.",
  descriptionEn: "Daily check of handling equipment.",
  aide: "Une anomalie immobilise l' engin.",
  aideEn: "A defect locks out the equipment.",
  lister: (params) => api.lister("magc-equipment-checks", params),
  creer: (data) => api.creer("magc-equipment-checks", data),
  modifier: (id, data) => api.modifier("magc-equipment-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("equipment", "Engin", "Equipment"),
    col("numero", "Numero", "Number"),
    col("controleur", "Controleur", "Checker"),
    col("date_controle", "Controle", "Checked at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("equipment", "Engin", "Equipment"),
    txt("numero", "Numero", "Number"),
    txt("controleur", "Controleur", "Checker"),
    dtx("date_controle", "Controle", "Checked at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcSafetyInspection: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "safety_inspection",
  tcode: "registre-safety-inspections",
  icon: Icons.ShieldCheck,
  titre: "Rondes de securite",
  titreEn: "Safety inspections",
  description: "Inspection periodique des zones du depot.",
  descriptionEn: "Periodic inspection of warehouse zones.",
  aide: "Le nombre d' anomalies qualifie la ronde.",
  aideEn: "Anomaly count qualifies the round.",
  lister: (params) => api.lister("magc-safety-inspections", params),
  creer: (data) => api.creer("magc-safety-inspections", data),
  modifier: (id, data) => api.modifier("magc-safety-inspections", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("zone", "Zone", "Zone"),
    col("inspecteur", "Inspecteur", "Inspector"),
    col("date", "Date", "Date"),
    col("anomalies", "Anomalies", "Anomalies"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("zone", "Zone", "Zone"),
    txt("inspecteur", "Inspecteur", "Inspector"),
    dtx("date", "Date", "Date"),
    num("anomalies", "Anomalies", "Anomalies"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcSpillCleanup: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "spill_cleanup",
  tcode: "registre-spill-cleanups",
  icon: Icons.Droplets,
  titre: "Nettoyages de deversement",
  titreEn: "Spill cleanups",
  description: "Traitement d' un deversement de produit.",
  descriptionEn: "Handling of a product spill.",
  aide: "Le produit et le volume dimensionnent l' intervention.",
  aideEn: "Product and volume size the response.",
  lister: (params) => api.lister("magc-spill-cleanups", params),
  creer: (data) => api.creer("magc-spill-cleanups", data),
  modifier: (id, data) => api.modifier("magc-spill-cleanups", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("zone", "Zone", "Zone"),
    col("produit", "Produit", "Product"),
    col("volume", "Volume", "Volume"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("zone", "Zone", "Zone"),
    txt("produit", "Produit", "Product"),
    num("volume", "Volume", "Volume"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcLoadingCheck: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "loading_check",
  tcode: "registre-loading-checks",
  icon: Icons.Truck,
  titre: "Controles de chargement",
  titreEn: "Loading checks",
  description: "Verification de la charge d' un camion avant depart.",
  descriptionEn: "Check of a truck load before departure.",
  aide: "Le nombre de colis charges doit egaler le bordereau.",
  aideEn: "Loaded parcels must match the manifest.",
  lister: (params) => api.lister("magc-loading-checks", params),
  creer: (data) => api.creer("magc-loading-checks", data),
  modifier: (id, data) => api.modifier("magc-loading-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("chargement", "Chargement", "Load"),
    col("camion", "Camion", "Truck"),
    col("nb_colis", "Nombre de colis", "Parcel count"),
    col("chargeur", "Chargeur", "Loader"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("chargement", "Chargement", "Load"),
    txt("camion", "Camion", "Truck"),
    num("nb_colis", "Nombre de colis", "Parcel count"),
    txt("chargeur", "Chargeur", "Loader"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcReceivingCheck: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "receiving_check",
  tcode: "registre-receiving-checks",
  icon: Icons.Package,
  titre: "Controles de reception",
  titreEn: "Receiving checks",
  description: "Verification de la marchandise entrante.",
  descriptionEn: "Check of inbound goods.",
  aide: "La conformite declenche la mise en stock.",
  aideEn: "Conformity triggers put-away.",
  lister: (params) => api.lister("magc-receiving-checks", params),
  creer: (data) => api.creer("magc-receiving-checks", data),
  modifier: (id, data) => api.modifier("magc-receiving-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("reception", "Reception", "Receipt"),
    col("fournisseur", "Fournisseur", "Supplier"),
    col("nb_colis", "Nombre de colis", "Parcel count"),
    col("conforme", "Conforme", "Conforming"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("reception", "Reception", "Receipt"),
    txt("fournisseur", "Fournisseur", "Supplier"),
    num("nb_colis", "Nombre de colis", "Parcel count"),
    chk("conforme", "Conforme", "Conforming"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcPutawayException: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "putaway_exception",
  tcode: "registre-putaway-exceptions",
  icon: Icons.AlertTriangle,
  titre: "Exceptions de rangement",
  titreEn: "Put-away exceptions",
  description: "Blocage constate lors d' une mise en place.",
  descriptionEn: "Blockage found during put-away.",
  aide: "Le type de probleme aiguille la resolution.",
  aideEn: "Problem type drives resolution.",
  lister: (params) => api.lister("magc-putaway-exceptions", params),
  creer: (data) => api.creer("magc-putaway-exceptions", data),
  modifier: (id, data) => api.modifier("magc-putaway-exceptions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("article", "Article", "Item"),
    col("emplacement", "Emplacement", "Location"),
    col("type_probleme", "Type de probleme", "Problem type"),
    col("signale_le", "Signale", "Flagged at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("article", "Article", "Item"),
    txt("emplacement", "Emplacement", "Location"),
    txt("type_probleme", "Type de probleme", "Problem type"),
    dtx("signale_le", "Signale", "Flagged at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcOrderStaging: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "order_staging",
  tcode: "registre-order-staging",
  icon: Icons.Boxes,
  titre: "Zone de pre-expedition",
  titreEn: "Order staging",
  description: "Préparation en zone de tri avant enlevement.",
  descriptionEn: "Prep in a staging area before collection.",
  aide: "Le nombre de lignes suivies caracterise la prepa.",
  aideEn: "Tracked line count characterizes staging.",
  lister: (params) => api.lister("magc-order-staging", params),
  creer: (data) => api.creer("magc-order-staging", data),
  modifier: (id, data) => api.modifier("magc-order-staging", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("commande", "Commande", "Order"),
    col("zone_prea", "Zone de preparation", "Staging zone"),
    col("nb_lignes", "Nombre de lignes", "Line count"),
    col("operateur", "Operateur", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("commande", "Commande", "Order"),
    txt("zone_prea", "Zone de preparation", "Staging zone"),
    num("nb_lignes", "Nombre de lignes", "Line count"),
    txt("operateur", "Operateur", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcColdChainCheck: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "cold_chain_check",
  tcode: "registre-cold-chain-checks",
  icon: Icons.Snowflake,
  titre: "Controles chaine du froid",
  titreEn: "Cold-chain checks",
  description: "Releve de temperature des chambres froides.",
  descriptionEn: "Temperature reading of cold rooms.",
  aide: "Hors plage = rupture de chaine a declarer.",
  aideEn: "Out of range = chain break to declare.",
  lister: (params) => api.lister("magc-cold-chain-checks", params),
  creer: (data) => api.creer("magc-cold-chain-checks", data),
  modifier: (id, data) => api.modifier("magc-cold-chain-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("chambre_froide", "Chambre froide", "Cold room"),
    col("temperature_c", "Temperature (C)", "Temperature (C)"),
    col("seuil_mini", "Seuil mini", "Min threshold"),
    col("seuil_maxi", "Seuil maxi", "Max threshold"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("chambre_froide", "Chambre froide", "Cold room"),
    num("temperature_c", "Temperature (C)", "Temperature (C)"),
    num("seuil_mini", "Seuil mini", "Min threshold"),
    num("seuil_maxi", "Seuil maxi", "Max threshold"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcHazmatHandling: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "hazmat_handling",
  tcode: "registre-hazmat-handling",
  icon: Icons.Biohazard,
  titre: "Manutention matieres dangereuses",
  titreEn: "Hazmat handling",
  description: "Prise en charge de matieres dangereuses.",
  descriptionEn: "Handling of dangerous goods.",
  aide: "La classe ADR conditionne les precautions.",
  aideEn: "The ADR class drives precautions.",
  lister: (params) => api.lister("magc-hazmat-handling", params),
  creer: (data) => api.creer("magc-hazmat-handling", data),
  modifier: (id, data) => api.modifier("magc-hazmat-handling", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("matiere", "Matiere", "Material"),
    col("classe", "Classe", "Class"),
    col("quantite", "Quantite", "Quantity"),
    col("operateur", "Operateur", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("matiere", "Matiere", "Material"),
    txt("classe", "Classe", "Class"),
    num("quantite", "Quantite", "Quantity"),
    txt("operateur", "Operateur", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagcDockAssignment: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "dock_assignment",
  tcode: "registre-dock-assignments",
  icon: Icons.CalendarClock,
  titre: "Affectations de quai",
  titreEn: "Dock assignments",
  description: "Attribution d' un quai et creneau pour une operation.",
  descriptionEn: "Assignment of a dock and slot for an operation.",
  aide: "Le respect du creneau evite l' engorgement des quais.",
  aideEn: "Keeping the slot avoids dock congestion.",
  lister: (params) => api.lister("magc-dock-assignments", params),
  creer: (data) => api.creer("magc-dock-assignments", data),
  modifier: (id, data) => api.modifier("magc-dock-assignments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("quai", "Quai", "Dock"),
    col("camion", "Camion", "Truck"),
    col("creneau", "Creneau", "Slot"),
    col("operateur", "Operateur", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("quai", "Quai", "Dock"),
    txt("camion", "Camion", "Truck"),
    dtx("creneau", "Creneau", "Slot"),
    txt("operateur", "Operateur", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};

