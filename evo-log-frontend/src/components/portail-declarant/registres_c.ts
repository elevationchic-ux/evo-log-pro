/**
 * Configs Registre pour portail-declarant (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-declarant");

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

export const registreDeclCustomsDeclaration: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "customs_declaration",
  tcode: "registre-customs-declarations",
  icon: Icons.ScrollText,
  titre: "Declarations en douane",
  titreEn: "Customs declarations",
  description: "Declaration detaillee deposee par le declarant pour une masse.",
  descriptionEn: "Detailed declaration filed by the declarant for a shipment.",
  aide: "Le regime douanier determine les droits dus.",
  aideEn: "The customs regime determines the duties owed.",
  lister: (params) => api.lister("decl-customs-declarations", params),
  creer: (data) => api.creer("decl-customs-declarations", data),
  modifier: (id, data) => api.modifier("decl-customs-declarations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("masse", "Masse", "Shipment"),
    col("regime", "Regime", "Regime"),
    col("valeur_douane", "Valeur en douane", "Customs value"),
    col("date_depot", "Date depot", "Filing date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("masse", "Masse", "Shipment"),
    txt("regime", "Regime", "Regime"),
    num("valeur_douane", "Valeur en douane", "Customs value"),
    dtx("date_depot", "Date depot", "Filing date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclHsClassification: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "hs_classification",
  tcode: "registre-hs-classifications",
  icon: Icons.Tags,
  titre: "Classifications douanieres (HS)",
  titreEn: "HS classifications",
  description: "Attribution du code SH/HS d' une marchandise.",
  descriptionEn: "Assignment of the HS code of a good.",
  aide: "Le code conditionne droits et reglementations.",
  aideEn: "The code conditions duties and regulations.",
  lister: (params) => api.lister("decl-hs-classifications", params),
  creer: (data) => api.creer("decl-hs-classifications", data),
  modifier: (id, data) => api.modifier("decl-hs-classifications", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("designation", "Designation", "Description"),
    col("code_hs", "Code SH", "HS code"),
    col("taux_droit", "Taux de droit", "Duty rate"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("designation", "Designation", "Description"),
    txt("code_hs", "Code SH", "HS code"),
    num("taux_droit", "Taux de droit", "Duty rate"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclOriginCertificate: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "origin_certificate",
  tcode: "registre-origin-certificates",
  icon: Icons.Award,
  titre: "Certificats d' origine",
  titreEn: "Origin certificates",
  description: "Justificatif d' origine preferentielle ou non d' une marchandise.",
  descriptionEn: "Proof of preferential or non-preferential origin.",
  aide: "Le type et le pays d' origine ouvrent un droit preferentiel.",
  aideEn: "Type and origin country open a preferential right.",
  lister: (params) => api.lister("decl-origin-certificates", params),
  creer: (data) => api.creer("decl-origin-certificates", data),
  modifier: (id, data) => api.modifier("decl-origin-certificates", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("type", "Type", "Type"),
    col("pays_origine", "Pays d' origine", "Origin country"),
    col("numero", "Numero", "Number"),
    col("date_emission", "Date emission", "Issue date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("type", "Type", "Type"),
    txt("pays_origine", "Pays d' origine", "Origin country"),
    txt("numero", "Numero", "Number"),
    dt("date_emission", "Date emission", "Issue date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclCustomsValuation: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "customs_valuation",
  tcode: "registre-customs-valuations",
  icon: Icons.Scale,
  titre: "Valeurs en douane",
  titreEn: "Customs valuations",
  description: "Determination de la valeur en douane d' une marchandise.",
  descriptionEn: "Determination of the customs value of a good.",
  aide: "La methode de valuation (transaction, identique...) conditionne la base.",
  aideEn: "The valuation method conditions the base.",
  lister: (params) => api.lister("decl-customs-valuations", params),
  creer: (data) => api.creer("decl-customs-valuations", data),
  modifier: (id, data) => api.modifier("decl-customs-valuations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("masse", "Masse", "Shipment"),
    col("methode", "Methode", "Method"),
    col("valeur", "Valeur", "Value"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("masse", "Masse", "Shipment"),
    txt("methode", "Methode", "Method"),
    num("valeur", "Valeur", "Value"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclIncotermsRecord: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "incoterms_record",
  tcode: "registre-incoterms-records",
  icon: Icons.Ship,
  titre: "Incoterms",
  titreEn: "Incoterms records",
  description: "Incoterm applicable a une operation d' import / export.",
  descriptionEn: "Incoterm applicable to an import/export operation.",
  aide: "L' incoterm repartit frais et transfert de risque.",
  aideEn: "The incoterm splits cost and risk transfer.",
  lister: (params) => api.lister("decl-incoterms-records", params),
  creer: (data) => api.creer("decl-incoterms-records", data),
  modifier: (id, data) => api.modifier("decl-incoterms-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("code", "Code", "Code"),
    col("lieu", "Lieu", "Place"),
    col("vendeur", "Vendeur", "Seller"),
    col("acheteur", "Acheteur", "Buyer"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("code", "Code", "Code"),
    txt("lieu", "Lieu", "Place"),
    txt("vendeur", "Vendeur", "Seller"),
    txt("acheteur", "Acheteur", "Buyer"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclImportLicense: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "import_license",
  tcode: "registre-import-licenses",
  icon: Icons.FileBadge,
  titre: "Licences d' importation",
  titreEn: "Import licenses",
  description: "Autorisation administrative d' importer certaines marchandises.",
  descriptionEn: "Administrative authorization to import certain goods.",
  aide: "Le quota et la validite bornent la licence.",
  aideEn: "Quota and validity bound the license.",
  lister: (params) => api.lister("decl-import-licenses", params),
  creer: (data) => api.creer("decl-import-licenses", data),
  modifier: (id, data) => api.modifier("decl-import-licenses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("produit", "Produit", "Product"),
    col("quota", "Quota", "Quota"),
    col("utilisable", "Utilise", "Used"),
    col("validite", "Validite", "Validity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    num("quota", "Quota", "Quota"),
    num("utilisable", "Utilise", "Used"),
    dt("validite", "Validite", "Validity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclExportLicense: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "export_license",
  tcode: "registre-export-licenses",
  icon: Icons.FileCheck2,
  titre: "Licences d' exportation",
  titreEn: "Export licenses",
  description: "Autorisation d' exporter des biens a double usage ou regulates.",
  descriptionEn: "Authorization to export dual-use or regulated goods.",
  aide: "La destination et la nature du bien conditionnent l' autorisation.",
  aideEn: "Destination and goods nature condition the authorization.",
  lister: (params) => api.lister("decl-export-licenses", params),
  creer: (data) => api.creer("decl-export-licenses", data),
  modifier: (id, data) => api.modifier("decl-export-licenses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("bien", "Bien", "Goods"),
    col("destination", "Destination", "Destination"),
    col("usage", "Usage", "Use"),
    col("validite", "Validite", "Validity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("bien", "Bien", "Goods"),
    txt("destination", "Destination", "Destination"),
    txt("usage", "Usage", "Use"),
    dt("validite", "Validite", "Validity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclPreClearance: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "pre_clearance",
  tcode: "registre-pre-clearance-submissions",
  icon: Icons.Hourglass,
  titre: "Pre-dedouanements",
  titreEn: "Pre-clearance submissions",
  description: "Depot anticipe du dossier pour fluidifier la sortie.",
  descriptionEn: "Advance filing to smooth the release.",
  aide: "Anticiper le depot reduit les temps d' immoobilisation.",
  aideEn: "Filing early reduces dwell time.",
  lister: (params) => api.lister("decl-pre-clearance-submissions", params),
  creer: (data) => api.creer("decl-pre-clearance-submissions", data),
  modifier: (id, data) => api.modifier("decl-pre-clearance-submissions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("masse", "Masse", "Shipment"),
    col("arrivee_prevue", "Arrivee prevue", "ETA"),
    col("depot", "Depot", "Submission"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("masse", "Masse", "Shipment"),
    dtx("arrivee_prevue", "Arrivee prevue", "ETA"),
    dtx("depot", "Depot", "Submission"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclCustomsInvoice: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "customs_invoice",
  tcode: "registre-customs-invoices",
  icon: Icons.Receipt,
  titre: "Factures commerciales",
  titreEn: "Customs invoices",
  description: "Facture commerciale jointe au dossier douanier.",
  descriptionEn: "Commercial invoice attached to the customs file.",
  aide: "La devise et la base (CIF/FOB) justifient la valeur.",
  aideEn: "Currency and basis (CIF/FOB) justify the value.",
  lister: (params) => api.lister("decl-customs-invoices", params),
  creer: (data) => api.creer("decl-customs-invoices", data),
  modifier: (id, data) => api.modifier("decl-customs-invoices", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("fournisseur", "Fournisseur", "Supplier"),
    col("montant", "Montant", "Amount"),
    col("devise", "Devise", "Currency"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("fournisseur", "Fournisseur", "Supplier"),
    num("montant", "Montant", "Amount"),
    txt("devise", "Devise", "Currency"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclPackingList: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "packing_list",
  tcode: "registre-packing-lists",
  icon: Icons.Boxes,
  titre: "Colisages douaniers",
  titreEn: "Customs packing lists",
  description: "Listage des colis d' une masse pour le controle douanier.",
  descriptionEn: "Parcel listing of a shipment for customs control.",
  aide: "Le nombre de colis doit correspondre au connaissement.",
  aideEn: "Parcel count must match the bill of lading.",
  lister: (params) => api.lister("decl-packing-lists", params),
  creer: (data) => api.creer("decl-packing-lists", data),
  modifier: (id, data) => api.modifier("decl-packing-lists", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("masse", "Masse", "Shipment"),
    col("nb_colis", "Nb colis", "Parcels"),
    col("poids_net", "Poids net", "Net weight"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("masse", "Masse", "Shipment"),
    num("nb_colis", "Nb colis", "Parcels"),
    num("poids_net", "Poids net", "Net weight"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclCertificateAnalysis: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "certificate_analysis",
  tcode: "registre-certificates-of-analysis",
  icon: Icons.FlaskConical,
  titre: "Certificats d' analyse",
  titreEn: "Certificates of analysis",
  description: "Analyse laboratoire attestant la conformite d' une marchandise.",
  descriptionEn: "Lab analysis attesting a good's conformity.",
  aide: "Les parametres analyzes prouvent la conformite normative.",
  aideEn: "Analyzed parameters prove normative conformity.",
  lister: (params) => api.lister("decl-certificates-of-analysis", params),
  creer: (data) => api.creer("decl-certificates-of-analysis", data),
  modifier: (id, data) => api.modifier("decl-certificates-of-analysis", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("produit", "Produit", "Product"),
    col("laboratoire", "Laboratoire", "Laboratory"),
    col("parametres", "Parametres", "Parameters"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    txt("laboratoire", "Laboratoire", "Laboratory"),
    txt("parametres", "Parametres", "Parameters"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclPhytosanitaryApp: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "phytosanitary_app",
  tcode: "registre-phytosanitary-applications",
  icon: Icons.BookMarked,
  titre: "Demandes phytosanitaires",
  titreEn: "Phytosanitary applications",
  description: "Demande de certificat phytosanitaire pour vegetaux/produits.",
  descriptionEn: "Request for a phytosanitary certificate for plants/products.",
  aide: "L' inspection conditionne la delivrance du certificat.",
  aideEn: "The inspection conditions the certificate issue.",
  lister: (params) => api.lister("decl-phytosanitary-applications", params),
  creer: (data) => api.creer("decl-phytosanitary-applications", data),
  modifier: (id, data) => api.modifier("decl-phytosanitary-applications", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("produit", "Produit", "Product"),
    col("destination", "Destination", "Destination"),
    col("date_controle", "Date controle", "Control date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    txt("destination", "Destination", "Destination"),
    dt("date_controle", "Date controle", "Control date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclCustomsPayment: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "customs_payment",
  tcode: "registre-customs-payments",
  icon: Icons.Banknote,
  titre: "Paiements douaniers",
  titreEn: "Customs payments",
  description: "Acquittement des droits et taxes de douane.",
  descriptionEn: "Settlement of customs duties and taxes.",
  aide: "Le montant paye doit egaler la liquidation.",
  aideEn: "The amount paid must equal the assessment.",
  lister: (params) => api.lister("decl-customs-payments", params),
  creer: (data) => api.creer("decl-customs-payments", data),
  modifier: (id, data) => api.modifier("decl-customs-payments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("declaration", "Declaration", "Declaration"),
    col("montant", "Montant", "Amount"),
    col("type_droit", "Type de droit", "Duty type"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("declaration", "Declaration", "Declaration"),
    num("montant", "Montant", "Amount"),
    txt("type_droit", "Type de droit", "Duty type"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclTransitDocument: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "transit_document",
  tcode: "registre-transit-documents",
  icon: Icons.Container,
  titre: "Documents de transit (T1/T2)",
  titreEn: "Transit documents (T1/T2)",
  description: "Document d' accompagnement d' un regime de transit.",
  descriptionEn: "Accompanying document of a transit regime.",
  aide: "Le dechargement au bureau d' arrivee clot le transit.",
  aideEn: "Discharge at the arrival office closes the transit.",
  lister: (params) => api.lister("decl-transit-documents", params),
  creer: (data) => api.creer("decl-transit-documents", data),
  modifier: (id, data) => api.modifier("decl-transit-documents", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("type", "Type", "Type"),
    col("bureau_depart", "Bureau de depart", "Departure office"),
    col("bureau_arrivee", "Bureau d' arrivee", "Arrival office"),
    col("garantie", "Garantie", "Guarantee"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("type", "Type", "Type"),
    txt("bureau_depart", "Bureau de depart", "Departure office"),
    txt("bureau_arrivee", "Bureau d' arrivee", "Arrival office"),
    num("garantie", "Garantie", "Guarantee"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclDangerousGoods: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "dangerous_goods_decl",
  tcode: "registre-dangerous-goods-decls",
  icon: Icons.Siren,
  titre: "Declarations marchandises dangereuses",
  titreEn: "Dangerous goods declarations",
  description: "Declaration ADR/IMDG d' une expedition de matieres dangereuses.",
  descriptionEn: "ADR/IMDG declaration of a dangerous goods shipment.",
  aide: "Le numero ONU et la classe conditionnent l' acceptation.",
  aideEn: "UN number and class condition acceptance.",
  lister: (params) => api.lister("decl-dangerous-goods-decls", params),
  creer: (data) => api.creer("decl-dangerous-goods-decls", data),
  modifier: (id, data) => api.modifier("decl-dangerous-goods-decls", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("numero_onu", "Numero ONU", "UN number"),
    col("classe", "Classe", "Class"),
    col("quantite", "Quantite", "Quantity"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("numero_onu", "Numero ONU", "UN number"),
    txt("classe", "Classe", "Class"),
    num("quantite", "Quantite", "Quantity"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclBondedWarehouseEntry: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "bonded_warehouse_entry",
  tcode: "registre-bonded-warehouse-entries",
  icon: Icons.Archive,
  titre: "Entrees en entrepot sous douane",
  titreEn: "Bonded warehouse entries",
  description: "Depot de marchandise sous controle douanier sans paiement immediat.",
  descriptionEn: "Storing goods under customs control without immediate payment.",
  aide: "La duree de sejour et la mise en libre prouve la sortie.",
  aideEn: "Stay duration and release prove the exit.",
  lister: (params) => api.lister("decl-bonded-warehouse-entries", params),
  creer: (data) => api.creer("decl-bonded-warehouse-entries", data),
  modifier: (id, data) => api.modifier("decl-bonded-warehouse-entries", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("entrepot", "Entrepot", "Warehouse"),
    col("masse", "Masse", "Shipment"),
    col("entree", "Entree", "Entry"),
    col("sortie_prevue", "Sortie prevue", "Planned exit"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("entrepot", "Entrepot", "Warehouse"),
    txt("masse", "Masse", "Shipment"),
    dtx("entree", "Entree", "Entry"),
    dtx("sortie_prevue", "Sortie prevue", "Planned exit"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclDutyReliefClaim: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "duty_relief_claim",
  tcode: "registre-duty-relief-claims",
  icon: Icons.Percent,
  titre: "Demandes de franchise de droits",
  titreEn: "Duty relief claims",
  description: "Demande d' exoneration ou de remboursement de droits.",
  descriptionEn: "Request for duty exemption or drawback.",
  aide: "Le motif (investissement, regime) justifie la franchise.",
  aideEn: "The reason (investment, regime) justifies the relief.",
  lister: (params) => api.lister("decl-duty-relief-claims", params),
  creer: (data) => api.creer("decl-duty-relief-claims", data),
  modifier: (id, data) => api.modifier("decl-duty-relief-claims", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("motif", "Motif", "Reason"),
    col("declaration", "Declaration", "Declaration"),
    col("montant_exonere", "Montant exonere", "Relieved amount"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("motif", "Motif", "Reason"),
    txt("declaration", "Declaration", "Declaration"),
    num("montant_exonere", "Montant exonere", "Relieved amount"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclManifestCorrection: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "manifest_correction",
  tcode: "registre-manifest-corrections",
  icon: Icons.FileWarning,
  titre: "Rectifications de manifeste",
  titreEn: "Manifest corrections",
  description: "Demande de rectification d' un manifeste de chargement.",
  descriptionEn: "Request to correct a loading manifest.",
  aide: "L' ecart constate doit etre motive et trace.",
  aideEn: "The observed variance must be justified and traced.",
  lister: (params) => api.lister("decl-manifest-corrections", params),
  creer: (data) => api.creer("decl-manifest-corrections", data),
  modifier: (id, data) => api.modifier("decl-manifest-corrections", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("manifeste", "Manifeste", "Manifest"),
    col("objet_rectification", "Objet de la rectification", "Correction object"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("manifeste", "Manifeste", "Manifest"),
    txt("objet_rectification", "Objet de la rectification", "Correction object"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeclCustomsAuditSupport: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "customs_audit_support",
  tcode: "registre-customs-audit-support",
  icon: Icons.FolderSearch,
  titre: "Support controle douanier",
  titreEn: "Customs audit support",
  description: "Dossier de pieces prepare pour un controle / verification douane.",
  descriptionEn: "Evidence pack prepared for a customs audit.",
  aide: "La completeness des pieces conditionne la levee du controle.",
  aideEn: "Document completeness conditions the audit closure.",
  lister: (params) => api.lister("decl-customs-audit-support", params),
  creer: (data) => api.creer("decl-customs-audit-support", data),
  modifier: (id, data) => api.modifier("decl-customs-audit-support", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("controle", "Controle", "Audit"),
    col("periode", "Periode", "Period"),
    col("pieces_fournies", "Pieces fournies", "Docs provided"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("controle", "Controle", "Audit"),
    txt("periode", "Periode", "Period"),
    num("pieces_fournies", "Pieces fournies", "Docs provided"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

