/**
 * Configs Registre pour transit-douane (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("transit-douane");

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

export const registreHsClassification: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "hs_classification",
  tcode: "registre-hs-classification",
  icon: Icons.BookOpen,
  titre: "Classification tarifaire SH",
  titreEn: "HS Tariff Classification",
  description: "Referentiel des codes du systeme harmonise appliques aux marchandises.",
  descriptionEn: "Harmonized System code reference applied to goods.",
  aide: "Chaque declaration d'origine doit pointer vers un code SH valide.",
  aideEn: "Each origin declaration must reference a valid HS code.",
  lister: (params) => api.lister("hs-classifications", params),
  creer: (data) => api.creer("hs-classifications", data),
  modifier: (id, data) => api.modifier("hs-classifications", id, data),
  unicite: "code_hs",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_hs", "Code SH", "HS code"),
    col("designation", "Designation officielle", "Official description"),
    col("section", "Section du SH", "HS section"),
    col("chapitre", "Chapitre", "Chapter"),
    col("position", "Position", "Heading"),
    col("sous_position", "Sous-position", "Subheading"),
    col("unite_mesure", "Unite officielle", "Official UoM"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_hs", "Code SH", "HS code", { requisCreation: true }),
    txt("designation", "Designation officielle", "Official description"),
    txt("section", "Section du SH", "HS section"),
    txt("chapitre", "Chapitre", "Chapter"),
    txt("position", "Position", "Heading"),
    txt("sous_position", "Sous-position", "Subheading"),
    txt("unite_mesure", "Unite officielle", "Official UoM"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreCustomsValuation: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "customs_valuation",
  tcode: "registre-customs-valuation",
  icon: Icons.Calculator,
  titre: "Valeur en douane / INCOTERMS",
  titreEn: "Customs valuation / INCOTERMS",
  description: "Determinations de valeur en douane selon accords OMC et INCOTERMS 2020.",
  descriptionEn: "Customs valuation per WTO agreement and INCOTERMS 2020.",
  aide: "Toute methode autre que transaction doit etre justifiee.",
  aideEn: "Any method other than transaction must be justified.",
  lister: (params) => api.lister("customs-valuations", params),
  creer: (data) => api.creer("customs-valuations", data),
  modifier: (id, data) => api.modifier("customs-valuations", id, data),
  unicite: "reference_dossier",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference_dossier", "Reference dossier", "File reference"),
    col("dum_id", "ID DUM", "DUM id"),
    col("methode_evaluation", "Methode d'evaluation", "Valuation method"),
    col("incoterm", "Incoterm", "Incoterm"),
    col("valeur_declaree_xaf", "Valeur declaree XAF", "Declared value XAF"),
    col("valeur_transport_xaf", "Fret XAF", "Freight XAF"),
    col("valeur_assurance_xaf", "Assurance XAF", "Insurance XAF"),
    col("valeur_douane_xaf", "Valeur en douane XAF", "Customs value XAF"),
    col("taux_change", "Taux de change applique", "Applied FX rate"),
    col("date_evaluation", "Date d'evaluation", "Valuation date"),
    col("justification", "Justification methode", "Method justification"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference_dossier", "Reference dossier", "File reference", { requisCreation: true }),
    num("dum_id", "ID DUM", "DUM id"),
    sel("methode_evaluation", "Methode d'evaluation", "Valuation method", "methode_evaluation"),
    txt("incoterm", "Incoterm", "Incoterm"),
    num("valeur_declaree_xaf", "Valeur declaree XAF", "Declared value XAF"),
    num("valeur_transport_xaf", "Fret XAF", "Freight XAF"),
    num("valeur_assurance_xaf", "Assurance XAF", "Insurance XAF"),
    num("valeur_douane_xaf", "Valeur en douane XAF", "Customs value XAF"),
    num("taux_change", "Taux de change applique", "Applied FX rate"),
    dt("date_evaluation", "Date d'evaluation", "Valuation date"),
    txt("justification", "Justification methode", "Method justification"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreOriginCertificate: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "origin_certificate",
  tcode: "registre-origin-certificates",
  icon: Icons.Award,
  titre: "Certificats d'origine",
  titreEn: "Origin certificates",
  description: "Form A, EUR.1, certificats CEMAC/CEA et declarations fournisseur.",
  descriptionEn: "Form A, EUR.1, CEMAC/CAS form and supplier declarations.",
  aide: "Verifier validite et visa de la chambre de commerce.",
  aideEn: "Verify validity and chamber of commerce visa.",
  lister: (params) => api.lister("origin-certificates", params),
  creer: (data) => api.creer("origin-certificates", data),
  modifier: (id, data) => api.modifier("origin-certificates", id, data),
  unicite: "numero_certificat",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_certificat", "Numero certificat", "Certificate number"),
    col("type_certificat", "Type de certificat", "Certificate type"),
    col("pays_origine", "Pays d'origine", "Country of origin"),
    col("exportateur", "Exportateur", "Exporter"),
    col("importateur", "Importateur", "Importer"),
    col("dum_id", "ID DUM", "DUM id"),
    col("date_emission", "Date d'emission", "Issue date"),
    col("date_expiration", "Date d'expiration", "Expiry date"),
    col("chambre_delivrance", "Chambre delivrance", "Issuing chamber"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_certificat", "Numero certificat", "Certificate number", { requisCreation: true }),
    sel("type_certificat", "Type de certificat", "Certificate type", "type_certificat"),
    txt("pays_origine", "Pays d'origine", "Country of origin"),
    txt("exportateur", "Exportateur", "Exporter"),
    txt("importateur", "Importateur", "Importer"),
    num("dum_id", "ID DUM", "DUM id"),
    dt("date_emission", "Date d'emission", "Issue date"),
    dt("date_expiration", "Date d'expiration", "Expiry date"),
    txt("chambre_delivrance", "Chambre delivrance", "Issuing chamber"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreBondedWarehouse: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "bonded_warehouse",
  tcode: "registre-bonded-warehouse",
  icon: Icons.Warehouse,
  titre: "Entrepots sous douane",
  titreEn: "Bonded warehouses",
  description: "Registre des entrepots sous douane agree et des marchandises stockees.",
  descriptionEn: "Registry of approved bonded warehouses and stored goods.",
  aide: "Chaque entrepot doit disposer d'un agrement en cours de validite.",
  aideEn: "Each warehouse must hold a valid approval.",
  lister: (params) => api.lister("bonded-warehouses", params),
  creer: (data) => api.creer("bonded-warehouses", data),
  modifier: (id, data) => api.modifier("bonded-warehouses", id, data),
  unicite: "code_entrepot",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_entrepot", "Code entrepot", "Warehouse code"),
    col("nom", "Nom", "Name"),
    col("agrement_numero", "Numero agrement", "Approval number"),
    col("date_debut_agrement", "Debut agrement", "Approval start"),
    col("date_fin_agrement", "Fin agrement", "Approval end"),
    col("capacite_m2", "Capacite m2", "Capacity m2"),
    col("localisation", "Localisation", "Location"),
    col("gestionnaire", "Gestionnaire", "Operator"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("code_entrepot", "Code entrepot", "Warehouse code", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("agrement_numero", "Numero agrement", "Approval number"),
    dt("date_debut_agrement", "Debut agrement", "Approval start"),
    dt("date_fin_agrement", "Fin agrement", "Approval end"),
    num("capacite_m2", "Capacite m2", "Capacity m2"),
    txt("localisation", "Localisation", "Location"),
    txt("gestionnaire", "Gestionnaire", "Operator"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreTransitGuarantee: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "transit_guarantee",
  tcode: "registre-transit-guarantees",
  icon: Icons.ShieldCheck,
  titre: "Cautions et garanties",
  titreEn: "Guarantees and bonds",
  description: "Cautions bancaires / garanties globale / individuelle pour operations en transit.",
  descriptionEn: "Bank bonds / global or individual guarantees for transit operations.",
  aide: "Le montant couvert doit depasser les droits eventuels.",
  aideEn: "The covered amount must exceed potential duties.",
  lister: (params) => api.lister("transit-guarantees", params),
  creer: (data) => api.creer("transit-guarantees", data),
  modifier: (id, data) => api.modifier("transit-guarantees", id, data),
  unicite: "reference_caution",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference_caution", "Reference caution", "Bond reference"),
    col("type_garantie", "Type garantie", "Guarantee type"),
    col("banque_emettrice", "Banque emettrice", "Issuing bank"),
    col("donneur_ordre", "Donneur d'ordre", "Orderer"),
    col("montant_caution_xaf", "Montant XAF", "Amount XAF"),
    col("date_debut", "Date debut", "Start date"),
    col("date_fin", "Date fin", "End date"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference_caution", "Reference caution", "Bond reference", { requisCreation: true }),
    sel("type_garantie", "Type garantie", "Guarantee type", "type_garantie"),
    txt("banque_emettrice", "Banque emettrice", "Issuing bank"),
    txt("donneur_ordre", "Donneur d'ordre", "Orderer"),
    num("montant_caution_xaf", "Montant XAF", "Amount XAF"),
    dt("date_debut", "Date debut", "Start date"),
    dt("date_fin", "Date fin", "End date"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreExportDeclaration: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "export_declaration",
  tcode: "registre-export-declarations",
  icon: Icons.PlaneTakeoff,
  titre: "Declarations export",
  titreEn: "Export declarations",
  description: "DGE / declarations d'exportation definitive ou temporaire.",
  descriptionEn: "Definitive or temporary export declarations.",
  aide: "Le certificat de sortie est edite apres validation de la DGE.",
  aideEn: "Exit certificate issued after DGE validation.",
  lister: (params) => api.lister("export-declarations", params),
  creer: (data) => api.creer("export-declarations", data),
  modifier: (id, data) => api.modifier("export-declarations", id, data),
  unicite: "numero_dge",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_dge", "Numero DGE", "DGE number"),
    col("declarant", "Declarant", "Declarant"),
    col("exportateur", "Exportateur", "Exporter"),
    col("pays_destination", "Pays de destination", "Destination country"),
    col("valeur_xaf", "Valeur XAF", "Value XAF"),
    col("poids_net_kg", "Poids net (kg)", "Net weight (kg)"),
    col("regime", "Regime", "Regime"),
    col("date_depot", "Date depot", "Filing date"),
    col("date_validation", "Date validation", "Validation date"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_dge", "Numero DGE", "DGE number", { requisCreation: true }),
    txt("declarant", "Declarant", "Declarant"),
    txt("exportateur", "Exportateur", "Exporter"),
    txt("pays_destination", "Pays de destination", "Destination country"),
    num("valeur_xaf", "Valeur XAF", "Value XAF"),
    num("poids_net_kg", "Poids net (kg)", "Net weight (kg)"),
    sel("regime", "Regime", "Regime", "regime"),
    dt("date_depot", "Date depot", "Filing date"),
    dt("date_validation", "Date validation", "Validation date"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreProhibitedGood: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "prohibited_good",
  tcode: "registre-prohibited-goods",
  icon: Icons.Ban,
  titre: "Marchandises prohibees / contingentees",
  titreEn: "Prohibited / restricted goods",
  description: "Liste des produits soumis a interdiction ou licence particuliere.",
  descriptionEn: "Products under prohibition or special license.",
  aide: "Chaque ligne declaree doit etre confrontee a cette liste.",
  aideEn: "Each declared line must be checked against this list.",
  lister: (params) => api.lister("prohibited-goods", params),
  creer: (data) => api.creer("prohibited-goods", data),
  modifier: (id, data) => api.modifier("prohibited-goods", id, data),
  unicite: "code_produit",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_produit", "Code produit", "Product code"),
    col("designation", "Designation", "Description"),
    col("code_hs", "Code SH associe", "Associated HS code"),
    col("categorie", "Categorie restriction", "Restriction category"),
    col("base_legale", "Base legale", "Legal basis"),
    col("autorite_competente", "Autorite competente", "Competent authority"),
    col("conditions_regime", "Conditions de levee", "Release conditions"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("code_produit", "Code produit", "Product code", { requisCreation: true }),
    txt("designation", "Designation", "Description"),
    txt("code_hs", "Code SH associe", "Associated HS code"),
    sel("categorie", "Categorie restriction", "Restriction category", "categorie"),
    txt("base_legale", "Base legale", "Legal basis"),
    txt("autorite_competente", "Autorite competente", "Competent authority"),
    txt("conditions_regime", "Conditions de levee", "Release conditions"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registreCustomsRegime: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "customs_regime",
  tcode: "registre-customs-regimes",
  icon: Icons.Settings,
  titre: "Regimes economiques",
  titreEn: "Economic customs regimes",
  description: "Admission temporaire, perfectionnement actif/passif, sous douane, exportation temporaire.",
  descriptionEn: "Temporary admission, inward/outward processing, bonded, temporary export.",
  aide: "Chaque regime necessite un arrete d'agrement.",
  aideEn: "Each regime requires an approval decree.",
  lister: (params) => api.lister("customs-regimes", params),
  creer: (data) => api.creer("customs-regimes", data),
  modifier: (id, data) => api.modifier("customs-regimes", id, data),
  unicite: "reference_regime",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference_regime", "Reference regime", "Regime reference"),
    col("dum_id", "ID DUM associe", "Linked DUM id"),
    col("type_regime", "Type de regime", "Regime type"),
    col("duree_max_mois", "Duree max (mois)", "Max duration (months)"),
    col("date_appllication", "Date d'application", "Application date"),
    col("date_echeance", "Date d'echeance", "Due date"),
    col("caution_associee", "Caution associee", "Related bond"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference_regime", "Reference regime", "Regime reference", { requisCreation: true }),
    num("dum_id", "ID DUM associe", "Linked DUM id"),
    sel("type_regime", "Type de regime", "Regime type", "type_regime"),
    num("duree_max_mois", "Duree max (mois)", "Max duration (months)"),
    dt("date_appllication", "Date d'application", "Application date"),
    dt("date_echeance", "Date d'echeance", "Due date"),
    txt("caution_associee", "Caution associee", "Related bond"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registrePhysicalInspection: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "physical_inspection",
  tcode: "registre-physical-inspections",
  icon: Icons.Search,
  titre: "Visites et inspections physiques",
  titreEn: "Physical inspections",
  description: "PV de visite douaniere, nivelles de controle, resultat.",
  descriptionEn: "Customs inspection report, control channel, result.",
  aide: "Le niveau de controle est attribue par le moteur de ciblage.",
  aideEn: "Control level is assigned by the targeting engine.",
  lister: (params) => api.lister("physical-inspections", params),
  creer: (data) => api.creer("physical-inspections", data),
  modifier: (id, data) => api.modifier("physical-inspections", id, data),
  unicite: "numero_pv",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_pv", "Numero PV", "Report number"),
    col("dum_id", "ID DUM", "DUM id"),
    col("canal", "Canal de controle", "Control channel"),
    col("inspecteur", "Inspecteur", "Inspector"),
    col("date_inspection", "Date inspection", "Inspection date"),
    col("lieu", "Lieu", "Location"),
    col("resultat", "Resultat", "Result"),
    col("ecart_poids_kg", "Ecart de poids", "Weight discrepancy"),
    col("ecart_colis", "Ecart colis", "Package discrepancy"),
    col("observations", "Observations", "Observations"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_pv", "Numero PV", "Report number", { requisCreation: true }),
    num("dum_id", "ID DUM", "DUM id"),
    sel("canal", "Canal de controle", "Control channel", "canal"),
    txt("inspecteur", "Inspecteur", "Inspector"),
    dtx("date_inspection", "Date inspection", "Inspection date"),
    txt("lieu", "Lieu", "Location"),
    sel("resultat", "Resultat", "Result", "resultat"),
    num("ecart_poids_kg", "Ecart de poids", "Weight discrepancy"),
    num("ecart_colis", "Ecart colis", "Package discrepancy"),
    txt("observations", "Observations", "Observations"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreDutyPayment: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "duty_payment",
  tcode: "registre-duty-payments",
  icon: Icons.Receipt,
  titre: "Paiement droits et taxes",
  titreEn: "Duty and tax payments",
  description: "Suivi des reglements (acomptes, solde, remboursement) associes aux DUM.",
  descriptionEn: "Payments tracking (advance, balance, refund) attached to DUMs.",
  aide: "Rapprochement avec la comptabilite obligatoire.",
  aideEn: "Reconciliation with accounting is mandatory.",
  lister: (params) => api.lister("duty-payments", params),
  creer: (data) => api.creer("duty-payments", data),
  modifier: (id, data) => api.modifier("duty-payments", id, data),
  unicite: "numero_quittance",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_quittance", "Numero quittance", "Receipt number"),
    col("dum_id", "ID DUM", "DUM id"),
    col("type_paiement", "Type paiement", "Payment type"),
    col("droits_percus_xaf", "Droits percus XAF", "Dues collected XAF"),
    col("tva_xaf", "TVA XAF", "VAT XAF"),
    col("taxe_statistique_xaf", "Taxe statistique XAF", "Statistical tax XAF"),
    col("redevance_id", "Redevance associee", "Related retribution"),
    col("mode_reglement", "Mode reglement", "Payment mode"),
    col("date_paiement", "Date paiement", "Payment date"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_quittance", "Numero quittance", "Receipt number", { requisCreation: true }),
    num("dum_id", "ID DUM", "DUM id"),
    sel("type_paiement", "Type paiement", "Payment type", "type_paiement"),
    num("droits_percus_xaf", "Droits percus XAF", "Dues collected XAF"),
    num("tva_xaf", "TVA XAF", "VAT XAF"),
    num("taxe_statistique_xaf", "Taxe statistique XAF", "Statistical tax XAF"),
    txt("redevance_id", "Redevance associee", "Related retribution"),
    sel("mode_reglement", "Mode reglement", "Payment mode", "mode_reglement"),
    dt("date_paiement", "Date paiement", "Payment date"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreTraderRegistration: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "trader_registration",
  tcode: "registre-trader-registration",
  icon: Icons.Contact,
  titre: "Enregistrement operateur economique",
  titreEn: "Economic operator registration",
  description: "Numeros operateur EORI local / agrements OEA.",
  descriptionEn: "Local EORI numbers / authorized economic operator approvals.",
  aide: "L'operateur doit etre a jour de ses obligations fiscales.",
  aideEn: "Operator must be up to date on tax obligations.",
  lister: (params) => api.lister("trader-registrations", params),
  creer: (data) => api.creer("trader-registrations", data),
  modifier: (id, data) => api.modifier("trader-registrations", id, data),
  unicite: "numero_operateur",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_operateur", "Numero operateur", "Operator number"),
    col("raison_sociale", "Raison sociale", "Legal name"),
    col("niu", "NIU", "Tax ID"),
    col("rc_number", "Numero RC", "Reg. commerce"),
    col("type_operateur", "Type operateur", "Operator type"),
    col("statut_oea", "Statut OEA", "AEO status"),
    col("date_agrement", "Date agrement", "Approval date"),
    col("date_expiration", "Date expiration", "Expiry date"),
    col("contact_email", "Email contact", "Contact email"),
    col("contact_telephone", "Telephone contact", "Contact phone"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_operateur", "Numero operateur", "Operator number", { requisCreation: true }),
    txt("raison_sociale", "Raison sociale", "Legal name"),
    txt("niu", "NIU", "Tax ID"),
    txt("rc_number", "Numero RC", "Reg. commerce"),
    sel("type_operateur", "Type operateur", "Operator type", "type_operateur"),
    sel("statut_oea", "Statut OEA", "AEO status", "statut_oea"),
    dt("date_agrement", "Date agrement", "Approval date"),
    dt("date_expiration", "Date expiration", "Expiry date"),
    txt("contact_email", "Email contact", "Contact email"),
    txt("contact_telephone", "Telephone contact", "Contact phone"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreTariffReference: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "tariff_reference",
  tcode: "registre-tariff-reference",
  icon: Icons.Scale,
  titre: "Tarif integre CEMAC",
  titreEn: "CEMAC integrated tariff",
  description: "Tarif exterieur commun CEMAC, taxes applicables par ligne tarifaire.",
  descriptionEn: "CEMAC common external tariff and applicable taxes.",
  aide: "Consulte automatiquement par le moteur de calcul DUM.",
  aideEn: "Auto-consulted by DUM calculation engine.",
  lister: (params) => api.lister("tariff-references", params),
  creer: (data) => api.creer("tariff-references", data),
  modifier: (id, data) => api.modifier("tariff-references", id, data),
  unicite: "code_ligne_tarifaire",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_ligne_tarifaire", "Code ligne tarifaire", "Tariff line code"),
    col("code_hs", "Code SH associe", "Associated HS"),
    col("designation", "Designation", "Description"),
    col("droit_base_pct", "Droit de base %", "Base duty %"),
    col("cotisation_compensatoire_pct", "Cotisation compensatrice %", "Comp. levy %"),
    col("taxe_foretiaire_pct", "Taxe forestiere %", "Forestry tax %"),
    col("redevance_statistique_pct", "Redevance statistique %", "Stat. levy %"),
    col("tva_pct", "TVA %", "VAT %"),
    col("categorie_produit", "Categorie produit", "Product category"),
    col("date_application", "Date d'application", "Application date"),
    col("date_fin", "Date de fin", "End date"),
  ],
  champs: [
    txt("code_ligne_tarifaire", "Code ligne tarifaire", "Tariff line code", { requisCreation: true }),
    txt("code_hs", "Code SH associe", "Associated HS"),
    txt("designation", "Designation", "Description"),
    num("droit_base_pct", "Droit de base %", "Base duty %"),
    num("cotisation_compensatoire_pct", "Cotisation compensatrice %", "Comp. levy %"),
    num("taxe_foretiaire_pct", "Taxe forestiere %", "Forestry tax %"),
    num("redevance_statistique_pct", "Redevance statistique %", "Stat. levy %"),
    num("tva_pct", "TVA %", "VAT %"),
    sel("categorie_produit", "Categorie produit", "Product category", "categorie_produit"),
    dt("date_application", "Date d'application", "Application date"),
    dt("date_fin", "Date de fin", "End date"),
  ],
};

