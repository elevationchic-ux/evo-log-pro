/**
 * Configs Registre pour finance-ohada (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("finance-ohada");

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

export const registreMultiyearBudget: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "budget_management",
  tcode: "registre-budget-management",
  icon: Icons.CalendarRange,
  titre: "Budget pluriannuel",
  titreEn: "Multi-year budget",
  description: "Budgets strategiques 3-5 ans.",
  descriptionEn: "3-5 year strategic budgets.",
  aide: "Vote en conseil d'administration.",
  aideEn: "Approved by the board.",
  lister: (params) => api.lister("multiyear-budgets", params),
  creer: (data) => api.creer("multiyear-budgets", data),
  modifier: (id, data) => api.modifier("multiyear-budgets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("exercice_debut", "Exercice debut", "Start year"),
    col("exercice_fin", "Exercice fin", "End year"),
    col("montant_prevu_xaf", "Montant prevu", "Planned amount"),
    col("axes_strategiques", "Axes strategiques", "Strategic axes"),
    col("vote_ba", "Vote BA", "Board approved"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("exercice_debut", "Exercice debut", "Start year"),
    num("exercice_fin", "Exercice fin", "End year"),
    num("montant_prevu_xaf", "Montant prevu", "Planned amount"),
    txt("axes_strategiques", "Axes strategiques", "Strategic axes"),
    chk("vote_ba", "Vote BA", "Board approved"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreCreditFacility: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "credit_facility",
  tcode: "registre-credit-facilities",
  icon: Icons.HandCoins,
  titre: "Facilites de caisse et credits",
  titreEn: "Cash credit facilities",
  description: "Facilites bancaires autorisees.",
  descriptionEn: "Authorized bank facilities.",
  aide: "Suivi de la consommation par rapport au plafond.",
  aideEn: "Track usage against limit.",
  lister: (params) => api.lister("credit-facilities", params),
  creer: (data) => api.creer("credit-facilities", data),
  modifier: (id, data) => api.modifier("credit-facilities", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("banque", "Banque", "Bank"),
    col("type_facilite", "Type", "Type"),
    col("montant_autorise_xaf", "Montant autorise", "Approved amount"),
    col("montant_utilise_xaf", "Montant utilise", "Used amount"),
    col("taux_interet_pct", "Taux interet %", "Interest %"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("banque", "Banque", "Bank"),
    sel("type_facilite", "Type", "Type", "type_facilite"),
    num("montant_autorise_xaf", "Montant autorise", "Approved amount"),
    num("montant_utilise_xaf", "Montant utilise", "Used amount"),
    num("taux_interet_pct", "Taux interet %", "Interest %"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreCashPool: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "cash_pooling",
  tcode: "registre-cash-pooling",
  icon: Icons.Layers,
  titre: "Centralisation de tresorerie",
  titreEn: "Cash pooling",
  description: "Pools de tresorerie inter-entites.",
  descriptionEn: "Inter-entity cash pools.",
  aide: "Compte rendu mensuel du pilotage.",
  aideEn: "Monthly treasury review.",
  lister: (params) => api.lister("cash-pools", params),
  creer: (data) => api.creer("cash-pools", data),
  modifier: (id, data) => api.modifier("cash-pools", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("entite_pilote", "Entite pilote", "Lead entity"),
    col("entites_participantes", "Entites participantes", "Participating entities"),
    col("montant_pool_xaf", "Montant pool", "Pool amount"),
    col("interet_intragroupe_pct", "Interet intragroupe %", "Intragroup interest %"),
    col("date_debut", "Debut", "Start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("entite_pilote", "Entite pilote", "Lead entity"),
    txt("entites_participantes", "Entites participantes", "Participating entities"),
    num("montant_pool_xaf", "Montant pool", "Pool amount"),
    num("interet_intragroupe_pct", "Interet intragroupe %", "Intragroup interest %"),
    dt("date_debut", "Debut", "Start"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreFinancialInvestment: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "investment_tracking",
  tcode: "registre-investment-tracking",
  icon: Icons.TrendingUp,
  titre: "Investissements financiers",
  titreEn: "Financial investments",
  description: "Placements, obligations, actions.",
  descriptionEn: "Deposits, bonds, equities.",
  aide: "Revue trimestrielle de performance.",
  aideEn: "Quarterly performance review.",
  lister: (params) => api.lister("financial-investments", params),
  creer: (data) => api.creer("financial-investments", data),
  modifier: (id, data) => api.modifier("financial-investments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_placement", "Type placement", "Investment type"),
    col("institution", "Institution", "Institution"),
    col("montant_place_xaf", "Montant place", "Amount placed"),
    col("rendement_attendu_pct", "Rendement attendu %", "Expected yield %"),
    col("date_debut", "Debut", "Start"),
    col("date_echeance", "Echeance", "Maturity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_placement", "Type placement", "Investment type", "type_placement"),
    txt("institution", "Institution", "Institution"),
    num("montant_place_xaf", "Montant place", "Amount placed"),
    num("rendement_attendu_pct", "Rendement attendu %", "Expected yield %"),
    dt("date_debut", "Debut", "Start"),
    dt("date_echeance", "Echeance", "Maturity"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreFxExposure: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "fx_management",
  tcode: "registre-fx-management",
  icon: Icons.DollarSign,
  titre: "Risque de change XAF/EUR/USD",
  titreEn: "FX exposure XAF/EUR/USD",
  description: "Expositions nettes par devise.",
  descriptionEn: "Net exposure per currency.",
  aide: "Couverture au-dela de seuil DAF.",
  aideEn: "Hedge above CFO threshold.",
  lister: (params) => api.lister("fx-exposures", params),
  creer: (data) => api.creer("fx-exposures", data),
  modifier: (id, data) => api.modifier("fx-exposures", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("devise", "Devise", "Currency"),
    col("exposition_nette", "Exposition nette", "Net exposure"),
    col("valeur_couverte", "Valeur couverte", "Hedged amount"),
    col("instrument_couverture", "Instrument", "Instrument"),
    col("taux_couverture_pct", "Taux couverture %", "Hedge ratio %"),
    col("date_echeance", "Echeance", "Maturity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("devise", "Devise", "Currency"),
    num("exposition_nette", "Exposition nette", "Net exposure"),
    num("valeur_couverte", "Valeur couverte", "Hedged amount"),
    sel("instrument_couverture", "Instrument", "Instrument", "instrument_couverture"),
    num("taux_couverture_pct", "Taux couverture %", "Hedge ratio %"),
    dt("date_echeance", "Echeance", "Maturity"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registrePaymentSchedule: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "payment_scheduling",
  tcode: "registre-payment-scheduling",
  icon: Icons.CalendarClock,
  titre: "Echeancier reglements fournisseurs",
  titreEn: "Supplier payment schedule",
  description: "Planned outbound payments.",
  descriptionEn: "Previsionnel des reglements fournisseurs.",
  aide: "Respect des delais de paiement loi HP.",
  aideEn: "Respect supplier payment legal delay.",
  lister: (params) => api.lister("payment-schedules", params),
  creer: (data) => api.creer("payment-schedules", data),
  modifier: (id, data) => api.modifier("payment-schedules", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("fournisseur_id", "Fournisseur", "Supplier"),
    col("facture_id", "Facture", "Invoice"),
    col("montant_echeance_xaf", "Montant", "Amount"),
    col("date_echeance", "Echeance", "Due date"),
    col("mode_reglement", "Mode reglement", "Payment mode"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("fournisseur_id", "Fournisseur", "Supplier"),
    num("facture_id", "Facture", "Invoice"),
    num("montant_echeance_xaf", "Montant", "Amount"),
    dt("date_echeance", "Echeance", "Due date"),
    sel("mode_reglement", "Mode reglement", "Payment mode", "mode_reglement"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreExpenseReport: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "expense_report",
  tcode: "registre-expense-reports",
  icon: Icons.Receipt,
  titre: "Notes de frais",
  titreEn: "Expense reports",
  description: "Remboursements de frais professionnel.",
  descriptionEn: "Business expense reimbursements.",
  aide: "Justificatifs obligatoires pour chaque ligne.",
  aideEn: "Receipt mandatory per line.",
  lister: (params) => api.lister("expense-reports", params),
  creer: (data) => api.creer("expense-reports", data),
  modifier: (id, data) => api.modifier("expense-reports", id, data),
  unicite: "numero_note_frais",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_note_frais", "Numero", "Number", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("periode", "Periode", "Period"),
    col("montant_total_xaf", "Montant total", "Total amount"),
    col("nb_justificatifs", "Nb justificatifs", "Receipt count"),
    col("date_depot", "Date depot", "Filing date"),
    col("validateur", "Validateur", "Approver"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_note_frais", "Numero", "Number", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    txt("periode", "Periode", "Period"),
    num("montant_total_xaf", "Montant total", "Total amount"),
    num("nb_justificatifs", "Nb justificatifs", "Receipt count"),
    dt("date_depot", "Date depot", "Filing date"),
    txt("validateur", "Validateur", "Approver"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registrePettyCashBox: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "petty_cash",
  tcode: "registre-petty-cash",
  icon: Icons.PiggyBank,
  titre: "Regies d'avance",
  titreEn: "Petty cash",
  description: "Caisse menue par point de service.",
  descriptionEn: "Cash float per location.",
  aide: "Reconciliation journaliere obligatoire.",
  aideEn: "Daily reconciliation mandatory.",
  lister: (params) => api.lister("petty-cash-boxes", params),
  creer: (data) => api.creer("petty-cash-boxes", data),
  modifier: (id, data) => api.modifier("petty-cash-boxes", id, data),
  unicite: "code_regie",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_regie", "Code regie", "Float code", { searchable: true }),
    col("lieu", "Lieu", "Location"),
    col("responsable", "Responsable", "Owner"),
    col("fond_initial_xaf", "Fond initial", "Initial float"),
    col("solde_actuel_xaf", "Solde actuel", "Current balance"),
    col("date_derniere_reconciliation", "Derniere recon.", "Last reconciliation"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_regie", "Code regie", "Float code", { obligatoire: true }),
    txt("lieu", "Lieu", "Location"),
    txt("responsable", "Responsable", "Owner"),
    num("fond_initial_xaf", "Fond initial", "Initial float"),
    num("solde_actuel_xaf", "Solde actuel", "Current balance"),
    dt("date_derniere_reconciliation", "Derniere recon.", "Last reconciliation"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreBankGuarantee: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "bank_guarantee",
  tcode: "registre-bank-guarantees",
  icon: Icons.Shield,
  titre: "Garanties bancaires",
  titreEn: "Bank guarantees",
  description: "Cautions emises par banque.",
  descriptionEn: "Bonds issued by banks.",
  aide: "Suivi strict des appels a premiere demande.",
  aideEn: "Track on-demand claims strictly.",
  lister: (params) => api.lister("bank-guarantees", params),
  creer: (data) => api.creer("bank-guarantees", data),
  modifier: (id, data) => api.modifier("bank-guarantees", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("banque_emettrice", "Banque emettrice", "Issuing bank"),
    col("beneficiaire", "Beneficiaire", "Beneficiary"),
    col("type_garantie", "Type", "Type"),
    col("montant_xaf", "Montant XAF", "Amount XAF"),
    col("commission_pct", "Commission %", "Fee %"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("banque_emettrice", "Banque emettrice", "Issuing bank"),
    txt("beneficiaire", "Beneficiaire", "Beneficiary"),
    sel("type_garantie", "Type", "Type", "type_garantie"),
    num("montant_xaf", "Montant XAF", "Amount XAF"),
    num("commission_pct", "Commission %", "Fee %"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreLeaseContract: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "lease_accounting",
  tcode: "registre-lease-accounting",
  icon: Icons.FileKey,
  titre: "Credit-leasing / contrats location",
  titreEn: "Lease and rental contracts",
  description: "Contrats leasing avec duree, loyer, valeur residuelle.",
  descriptionEn: "Lease contracts with term, payment, residual.",
  aide: "Conforme OHADA / IFRS 16.",
  aideEn: "OHADA / IFRS 16 compliant.",
  lister: (params) => api.lister("lease-contracts", params),
  creer: (data) => api.creer("lease-contracts", data),
  modifier: (id, data) => api.modifier("lease-contracts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_contrat", "Type", "Type"),
    col("bien_concerne", "Bien concerne", "Asset"),
    col("loyer_mensuel_xaf", "Loyer mensuel", "Monthly payment"),
    col("duree_mois", "Duree (mois)", "Term (months)"),
    col("valeur_residuelle_xaf", "Valeur residuelle", "Residual value"),
    col("date_debut", "Debut", "Start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_contrat", "Type", "Type", "type_contrat"),
    txt("bien_concerne", "Bien concerne", "Asset"),
    num("loyer_mensuel_xaf", "Loyer mensuel", "Monthly payment"),
    num("duree_mois", "Duree (mois)", "Term (months)"),
    num("valeur_residuelle_xaf", "Valeur residuelle", "Residual value"),
    dt("date_debut", "Debut", "Start"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreCashForecast: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "financial_forecast",
  tcode: "registre-financial-forecast",
  icon: Icons.TrendingUp,
  titre: "Previsions de tresorerie",
  titreEn: "Cash forecast",
  description: "Projection de tresorerie 12-24 mois.",
  descriptionEn: "12-24 month cash projection.",
  aide: "Revue hebdomadaire par tresorier.",
  aideEn: "Weekly review by treasurer.",
  lister: (params) => api.lister("cash-forecasts", params),
  creer: (data) => api.creer("cash-forecasts", data),
  modifier: (id, data) => api.modifier("cash-forecasts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("horizon_mois", "Horizon (mois)", "Horizon (months)"),
    col("entree_attendue_xaf", "Entrees attendues", "Expected inflow"),
    col("sortie_attendue_xaf", "Sorties attendues", "Expected outflow"),
    col("tresorerie_projete_xaf", "Tresorerie projetee", "Projected cash"),
    col("hypothese", "Hypotheses", "Assumptions"),
    col("date_revision", "Revision", "Revision date"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("horizon_mois", "Horizon (mois)", "Horizon (months)"),
    num("entree_attendue_xaf", "Entrees attendues", "Expected inflow"),
    num("sortie_attendue_xaf", "Sorties attendues", "Expected outflow"),
    num("tresorerie_projete_xaf", "Tresorerie projetee", "Projected cash"),
    txt("hypothese", "Hypotheses", "Assumptions"),
    dt("date_revision", "Revision", "Revision date"),
  ],
};


export const registreTreasuryAlert: ConfigRegistre = {
  permModule: "finance",
  permSousModule: "treasury_alerts",
  tcode: "registre-treasury-alerts",
  icon: Icons.BellRing,
  titre: "Alertes tresorerie",
  titreEn: "Treasury alerts",
  description: "Alertes seuil, BFR, echeance.",
  descriptionEn: "Threshold, WC, due date alerts.",
  aide: "Escalade DAF en cas de depassement seuil.",
  aideEn: "Escalate to CFO if threshold crossed.",
  lister: (params) => api.lister("treasury-alerts", params),
  creer: (data) => api.creer("treasury-alerts", data),
  modifier: (id, data) => api.modifier("treasury-alerts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_alerte", "Type", "Type"),
    col("seuil_declencheur", "Seuil declencheur", "Trigger threshold"),
    col("valeur_constatee", "Valeur constatee", "Observed value"),
    col("date_alerte", "Date", "Alert date"),
    col("destinataire", "Destinataire", "Recipient"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_alerte", "Type", "Type", "type_alerte"),
    num("seuil_declencheur", "Seuil declencheur", "Trigger threshold"),
    num("valeur_constatee", "Valeur constatee", "Observed value"),
    dtx("date_alerte", "Date", "Alert date"),
    txt("destinataire", "Destinataire", "Recipient"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};

