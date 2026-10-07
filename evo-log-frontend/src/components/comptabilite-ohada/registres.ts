/**
 * Configs Registre pour comptabilite-ohada (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("comptabilite-ohada");

function col(key: string, header: string, headerEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {
  return { key, header, headerEn, ...opts } as ColonneRegistre;
}

function txt(key: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { key, label, labelEn, type: "text", ...opts } as ChampRegistre;
}

function num(key: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { key, label, labelEn, type: "number", ...opts } as ChampRegistre;
}

function dt(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "date" } as ChampRegistre;
}

function dtx(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "datetime-local" } as ChampRegistre;
}

function area(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "textarea" } as ChampRegistre;
}

function chk(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "checkbox" } as ChampRegistre;
}

function sel(key: string, label: string, labelEn: string, nomKey: string): ChampRegistre {
  return { key, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;
}

function filtreSel(key: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {
  return { key, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;
}

export const registreAssetRegistration: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "fixed_asset",
  tcode: "registre-fixed-assets",
  icon: Icons.Building,
  titre: "Registre immobilisations",
  titreEn: "Fixed asset register",
  description: "Biens inscrits a l'actif avec valeur amortissable.",
  descriptionEn: "Assets recorded with amortizable value.",
  aide: "Chaque bien recoit un numero d'inventaire.",
  aideEn: "Each asset has an inventory number.",
  lister: (params) => api.lister("asset-registrations", params),
  creer: (data) => api.creer("asset-registrations", data),
  modifier: (id, data) => api.modifier("asset-registrations", id, data),
  unicite: "numero_inventaire",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_inventaire", "Numero inventaire", "Inventory number", { searchable: true }),
    col("designation", "Designation", "Description"),
    col("categorie", "Categorie OHADA", "OHADA category"),
    col("date_acquisition", "Date acquisition", "Acquisition date"),
    col("valeur_acquisition_xaf", "Valeur acquisition", "Acquisition value"),
    col("valeur_residuelle_xaf", "Valeur residuelle", "Residual value"),
    col("duree_amortissement_an", "Duree (ans)", "Useful life (y)"),
    col("mode_amortissement", "Mode amortissement", "Amortization"),
    col("compte_immo", "Compte OHADA", "OHADA account"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_inventaire", "Numero inventaire", "Inventory number", { obligatoire: true }),
    txt("designation", "Designation", "Description"),
    sel("categorie", "Categorie OHADA", "OHADA category", "categorie"),
    dt("date_acquisition", "Date acquisition", "Acquisition date"),
    num("valeur_acquisition_xaf", "Valeur acquisition", "Acquisition value"),
    num("valeur_residuelle_xaf", "Valeur residuelle", "Residual value"),
    num("duree_amortissement_an", "Duree (ans)", "Useful life (y)"),
    sel("mode_amortissement", "Mode amortissement", "Amortization", "mode_amortissement"),
    txt("compte_immo", "Compte OHADA", "OHADA account"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreDepreciationSchedule: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "depreciation",
  tcode: "registre-depreciation-schedules",
  icon: Icons.CalendarClock,
  titre: "Plans d'amortissement",
  titreEn: "Depreciation schedules",
  description: "Echeancier annuel par immobilisation.",
  descriptionEn: "Annual schedule per asset.",
  aide: "Le plan est inchange pendant l'exercice.",
  aideEn: "Schedule is unchanged during the fiscal year.",
  lister: (params) => api.lister("depreciation-schedules", params),
  creer: (data) => api.creer("depreciation-schedules", data),
  modifier: (id, data) => api.modifier("depreciation-schedules", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("asset_id", "Immobilisation", "Asset"),
    col("exercice", "Exercice", "Fiscal year"),
    col("dotation_xaf", "Dotation", "Charge"),
    col("cumul_xaf", "Cumul", "Accumulated"),
    col("valeur_nette_xaf", "Valeur nette", "Net value"),
    col("date_ecriture", "Date ecriture", "Posting date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("asset_id", "Immobilisation", "Asset"),
    num("exercice", "Exercice", "Fiscal year"),
    num("dotation_xaf", "Dotation", "Charge"),
    num("cumul_xaf", "Cumul", "Accumulated"),
    num("valeur_nette_xaf", "Valeur nette", "Net value"),
    dt("date_ecriture", "Date ecriture", "Posting date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreProvision: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "provision",
  tcode: "registre-provisions",
  icon: Icons.ShieldAlert,
  titre: "Dotations et reprises",
  titreEn: "Provision charges and reversals",
  description: "Provisions pour risque / depreciation.",
  descriptionEn: "Risk or impairment provisions.",
  aide: "Justification comptable obligatoire.",
  aideEn: "Accounting justification mandatory.",
  lister: (params) => api.lister("provisions", params),
  creer: (data) => api.creer("provisions", data),
  modifier: (id, data) => api.modifier("provisions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_provision", "Type", "Type"),
    col("exercice", "Exercice", "Fiscal year"),
    col("montant_xaf", "Montant XAF", "Amount XAF"),
    col("date_constat", "Date constat", "Recognition date"),
    col("compte_charge", "Compte charge", "Expense account"),
    col("comporte_passif", "Compte passif", "Liability account"),
    col("statut", "Statut", "Status"),
    col("motivation", "Motivation", "Motivation"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_provision", "Type", "Type", "type_provision"),
    num("exercice", "Exercice", "Fiscal year"),
    num("montant_xaf", "Montant XAF", "Amount XAF"),
    dt("date_constat", "Date constat", "Recognition date"),
    txt("compte_charge", "Compte charge", "Expense account"),
    txt("comporte_passif", "Compte passif", "Liability account"),
    sel("statut", "Statut", "Status", "statut"),
    txt("motivation", "Motivation", "Motivation"),
  ],
};


export const registreBankReconciliation: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "bank_reconciliation",
  tcode: "registre-bank-reconciliation",
  icon: Icons.Landmark,
  titre: "Rapprochement bancaire",
  titreEn: "Bank reconciliation",
  description: "Pointages banque / compta par periode.",
  descriptionEn: "Bank / GL matching per period.",
  aide: "Un ecart doit etre explique avant cloture.",
  aideEn: "Discrepancy explained before close.",
  lister: (params) => api.lister("bank-reconciliations", params),
  creer: (data) => api.creer("bank-reconciliations", data),
  modifier: (id, data) => api.modifier("bank-reconciliations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("compte_banque", "Compte bancaire", "Bank account"),
    col("periode_debut", "Debut", "Start"),
    col("periode_fin", "Fin", "End"),
    col("solde_banque_xaf", "Solde banque", "Bank balance"),
    col("solde_compta_xaf", "Solde compta", "GL balance"),
    col("ecart_xaf", "Ecart", "Discrepancy"),
    col("nb_lignes_pointees", "Lignes pointees", "Matched lines"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("compte_banque", "Compte bancaire", "Bank account"),
    dt("periode_debut", "Debut", "Start"),
    dt("periode_fin", "Fin", "End"),
    num("solde_banque_xaf", "Solde banque", "Bank balance"),
    num("solde_compta_xaf", "Solde compta", "GL balance"),
    num("ecart_xaf", "Ecart", "Discrepancy"),
    num("nb_lignes_pointees", "Lignes pointees", "Matched lines"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreIntercompanyEntry: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "intercompany",
  tcode: "registre-intercompany",
  icon: Icons.Link,
  titre: "Comptes inter-societes",
  titreEn: "Intercompany accounts",
  description: "Echanges entre entites du groupe.",
  descriptionEn: "Transactions between group entities.",
  aide: "Elimination en consolidation obligatoire.",
  aideEn: "Elimination in consolidation is mandatory.",
  lister: (params) => api.lister("intercompany-entries", params),
  creer: (data) => api.creer("intercompany-entries", data),
  modifier: (id, data) => api.modifier("intercompany-entries", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("entite_emettrice", "Entite emettrice", "Origin entity"),
    col("entite_destinatrice", "Entite destinatrice", "Destination entity"),
    col("date_ecriture", "Date", "Date"),
    col("montant_xaf", "Montant XAF", "Amount XAF"),
    col("nature", "Nature", "Nature"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("entite_emettrice", "Entite emettrice", "Origin entity"),
    txt("entite_destinatrice", "Entite destinatrice", "Destination entity"),
    dt("date_ecriture", "Date", "Date"),
    num("montant_xaf", "Montant XAF", "Amount XAF"),
    sel("nature", "Nature", "Nature", "nature"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreBudgetControl: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "budget_control",
  tcode: "registre-budget-control",
  icon: Icons.Wallet,
  titre: "Budget et controle budgetaire",
  titreEn: "Budget and control",
  description: "Budgets par centre de cout, consommations, ecarts.",
  descriptionEn: "Budgets per cost center, consumption, variance.",
  aide: "Le depassement declenche alerte DAF.",
  aideEn: "Overrun triggers CFO alert.",
  lister: (params) => api.lister("budget-controls", params),
  creer: (data) => api.creer("budget-controls", data),
  modifier: (id, data) => api.modifier("budget-controls", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("centre_cout", "Centre de cout", "Cost center"),
    col("exercice", "Exercice", "Fiscal year"),
    col("budget_prevu_xaf", "Budget prevu", "Planned budget"),
    col("consomme_xaf", "Consomme", "Consumed"),
    col("engagement_xaf", "Engage", "Committed"),
    col("ecart_pct", "Ecart %", "Variance %"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("centre_cout", "Centre de cout", "Cost center"),
    num("exercice", "Exercice", "Fiscal year"),
    num("budget_prevu_xaf", "Budget prevu", "Planned budget"),
    num("consomme_xaf", "Consomme", "Consumed"),
    num("engagement_xaf", "Engage", "Committed"),
    num("ecart_pct", "Ecart %", "Variance %"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreAuditPaf: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "audit_trail",
  tcode: "registre-audit-trail",
  icon: Icons.Lock,
  titre: "Piste d'audit fiable",
  titreEn: "Reliable audit trail",
  description: "Journal inalterable des ecritures comptables.",
  descriptionEn: "Tamper-proof journal of GL entries.",
  aide: "Chaque modification est une nouvelle ligne.",
  aideEn: "Any modification is a new line.",
  lister: (params) => api.lister("audit-pafs", params),
  creer: (data) => api.creer("audit-pafs", data),
  modifier: (id, data) => api.modifier("audit-pafs", id, data),
  unicite: "hash_ligne",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("hash_ligne", "Hash ligne", "Row hash", { searchable: true }),
    col("date_ecriture", "Date ecriture", "Posting date"),
    col("numero_piece", "Numero piece", "Document number"),
    col("compte", "Compte", "Account"),
    col("libelle", "Libelle", "Label"),
    col("debit_xaf", "Debit", "Debit"),
    col("credit_xaf", "Credit", "Credit"),
    col("hash_precedent", "Hash precedent", "Previous hash"),
    col("validite", "Validite PAF", "PAF valid"),
  ],
  champs: [
    txt("hash_ligne", "Hash ligne", "Row hash", { obligatoire: true }),
    dt("date_ecriture", "Date ecriture", "Posting date"),
    txt("numero_piece", "Numero piece", "Document number"),
    txt("compte", "Compte", "Account"),
    txt("libelle", "Libelle", "Label"),
    num("debit_xaf", "Debit", "Debit"),
    num("credit_xaf", "Credit", "Credit"),
    txt("hash_precedent", "Hash precedent", "Previous hash"),
    chk("validite", "Validite PAF", "PAF valid"),
  ],
};


export const registreTaxDeclaration: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "tax_declaration",
  tcode: "registre-tax-declarations",
  icon: Icons.FileSignature,
  titre: "Declarations fiscales periodiques",
  titreEn: "Periodic tax filings",
  description: "TVA, IS, IRGM, patente.",
  descriptionEn: "VAT, CIT, PAYE, license.",
  aide: "Dépot dans le delai legal sous peine de penalite.",
  aideEn: "Filed within legal deadline or penalties apply.",
  lister: (params) => api.lister("tax-declarations", params),
  creer: (data) => api.creer("tax-declarations", data),
  modifier: (id, data) => api.modifier("tax-declarations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_declaration", "Type declaration", "Tax type"),
    col("periode_debut", "Debut periode", "Period start"),
    col("periode_fin", "Fin periode", "Period end"),
    col("base_imposable_xaf", "Base imposable", "Tax base"),
    col("droits_xaf", "Droits", "Duties"),
    col("date_depot", "Date depot", "Filing date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_declaration", "Type declaration", "Tax type", "type_declaration"),
    dt("periode_debut", "Debut periode", "Period start"),
    dt("periode_fin", "Fin periode", "Period end"),
    num("base_imposable_xaf", "Base imposable", "Tax base"),
    num("droits_xaf", "Droits", "Duties"),
    dt("date_depot", "Date depot", "Filing date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registrePayrollEntry: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "payroll_accounts",
  tcode: "registre-payroll-accounts",
  icon: Icons.Users,
  titre: "Ecritures de paie",
  titreEn: "Payroll entries",
  description: "Journalisation de la paie par periode.",
  descriptionEn: "Payroll booking per period.",
  aide: "Rapproche du livre de paie RH.",
  aideEn: "Matches RH payroll book.",
  lister: (params) => api.lister("payroll-entries", params),
  creer: (data) => api.creer("payroll-entries", data),
  modifier: (id, data) => api.modifier("payroll-entries", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("periode", "Periode", "Period"),
    col("masse_salariale_xaf", "Masse salariale", "Payroll mass"),
    col("charges_patronales_xaf", "Charges patronales", "Employer taxes"),
    col("impot_retenu_xaf", "Impot retenu", "Withheld tax"),
    col("net_paye_xaf", "Net paye", "Net paid"),
    col("date_passage", "Date passage", "Posting date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("periode", "Periode", "Period"),
    num("masse_salariale_xaf", "Masse salariale", "Payroll mass"),
    num("charges_patronales_xaf", "Charges patronales", "Employer taxes"),
    num("impot_retenu_xaf", "Impot retenu", "Withheld tax"),
    num("net_paye_xaf", "Net paye", "Net paid"),
    dt("date_passage", "Date passage", "Posting date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreTreasuryAccount: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "treasury_accounts",
  tcode: "registre-treasury-accounts",
  icon: Icons.Vault,
  titre: "Comptes de tresorerie",
  titreEn: "Treasury accounts",
  description: "Comptes banque / caisse / regies.",
  descriptionEn: "Bank / cash / petty accounts.",
  aide: "Chaque compte a un responsable nomme.",
  aideEn: "Each account has a designated owner.",
  lister: (params) => api.lister("treasury-accounts", params),
  creer: (data) => api.creer("treasury-accounts", data),
  modifier: (id, data) => api.modifier("treasury-accounts", id, data),
  unicite: "code_compte",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_compte", "Code compte", "Account code", { searchable: true }),
    col("intitule", "Intitule", "Title"),
    col("type_compte", "Type", "Type"),
    col("banque", "Banque", "Bank"),
    col("rib", "RIB", "IBAN"),
    col("solde_actuel_xaf", "Solde actuel", "Current balance"),
    col("devise", "Devise", "Currency"),
    col("responsable", "Responsable", "Owner"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_compte", "Code compte", "Account code", { obligatoire: true }),
    txt("intitule", "Intitule", "Title"),
    sel("type_compte", "Type", "Type", "type_compte"),
    txt("banque", "Banque", "Bank"),
    txt("rib", "RIB", "IBAN"),
    num("solde_actuel_xaf", "Solde actuel", "Current balance"),
    txt("devise", "Devise", "Currency"),
    txt("responsable", "Responsable", "Owner"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreAnalyticalSection: ConfigRegistre = {
  permModule: "compta",
  permSousModule: "analytical_accounting",
  tcode: "registre-analytical-accounting",
  icon: Icons.Split,
  titre: "Comptabilite analytique",
  titreEn: "Cost accounting",
  description: "Sections analytiques par activite.",
  descriptionEn: "Cost sections per activity.",
  aide: "Cles de repartition validees par DAF.",
  aideEn: "Allocation keys approved by CFO.",
  lister: (params) => api.lister("analytical-sections", params),
  creer: (data) => api.creer("analytical-sections", data),
  modifier: (id, data) => api.modifier("analytical-sections", id, data),
  unicite: "code_section",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_section", "Code section", "Section code", { searchable: true }),
    col("intitule", "Intitule", "Title"),
    col("type_section", "Type", "Type"),
    col("cle_repartition", "Cle de repartition", "Allocation key"),
    col("unite_oeuvre", "Unite d'oeuvre", "Cost driver"),
    col("cout_total_xaf", "Cout total", "Total cost"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("code_section", "Code section", "Section code", { obligatoire: true }),
    txt("intitule", "Intitule", "Title"),
    sel("type_section", "Type", "Type", "type_section"),
    txt("cle_repartition", "Cle de repartition", "Allocation key"),
    txt("unite_oeuvre", "Unite d'oeuvre", "Cost driver"),
    num("cout_total_xaf", "Cout total", "Total cost"),
    chk("actif", "Actif", "Active"),
  ],
};

