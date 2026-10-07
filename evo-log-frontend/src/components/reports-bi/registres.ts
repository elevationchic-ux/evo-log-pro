/**
 * Configs Registre pour reports-bi (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("reports-bi");

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

export const registreWarehouseTable: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "data_warehouse",
  tcode: "registre-data-warehouse",
  icon: Icons.Database,
  titre: "Entrepot de donnees",
  titreEn: "Data warehouse",
  description: "Tables ETL et cubes OLAP.",
  descriptionEn: "ETL tables and OLAP cubes.",
  aide: "Fraicheur maximale : 24h.",
  aideEn: "Max freshness: 24h.",
  lister: (params) => api.lister("warehouse-tables", params),
  creer: (data) => api.creer("warehouse-tables", data),
  modifier: (id, data) => api.modifier("warehouse-tables", id, data),
  unicite: "code_table",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_table", "Code table", "Table code"),
    col("domaine", "Domaine", "Domain"),
    col("frequence_refresh", "Refresh", "Refresh"),
    col("volume_lignes", "Volume lignes", "Row count"),
    col("dernier_refresh", "Dernier refresh", "Last refresh"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_table", "Code table", "Table code", { requisCreation: true }),
    txt("domaine", "Domaine", "Domain"),
    sel("frequence_refresh", "Refresh", "Refresh", "frequence_refresh"),
    num("volume_lignes", "Volume lignes", "Row count"),
    dtx("dernier_refresh", "Dernier refresh", "Last refresh"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreScorecard: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "scorecard",
  tcode: "registre-scorecards",
  icon: Icons.Target,
  titre: "Tableaux de score par pole",
  titreEn: "Scorecards per pole",
  description: "KPI consolides par direction.",
  descriptionEn: "KPIs consolidated per department.",
  aide: "Revue mensuelle direction.",
  aideEn: "Monthly leadership review.",
  lister: (params) => api.lister("scorecards", params),
  creer: (data) => api.creer("scorecards", data),
  modifier: (id, data) => api.modifier("scorecards", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("pole", "Pole", "Pole"),
    col("periode", "Periode", "Period"),
    col("nb_kpis", "Nb KPI", "KPI count"),
    col("score_global_pct", "Score global %", "Overall score %"),
    col("kpis_rouges", "KPI rouges", "Red KPIs"),
    col("kpis_oranges", "KPI oranges", "Orange KPIs"),
    col("kpis_verts", "KPI verts", "Green KPIs"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("pole", "Pole", "Pole"),
    txt("periode", "Periode", "Period"),
    num("nb_kpis", "Nb KPI", "KPI count"),
    num("score_global_pct", "Score global %", "Overall score %"),
    num("kpis_rouges", "KPI rouges", "Red KPIs"),
    num("kpis_oranges", "KPI oranges", "Orange KPIs"),
    num("kpis_verts", "KPI verts", "Green KPIs"),
  ],
};


export const registreIndustryBenchmark: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "benchmark",
  tcode: "registre-benchmarks",
  icon: Icons.GitCompare,
  titre: "Comparaison sectorielle ports CEMAC",
  titreEn: "CEMAC port benchmarks",
  description: "Indicateurs compares aux ports voisins.",
  descriptionEn: "Metrics vs neighboring ports.",
  aide: "Sources officielles seulement.",
  aideEn: "Official sources only.",
  lister: (params) => api.lister("industry-benchmarks", params),
  creer: (data) => api.creer("industry-benchmarks", data),
  modifier: (id, data) => api.modifier("industry-benchmarks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("indicateur", "Indicateur", "Indicator"),
    col("valeur_interne", "Valeur interne", "Internal value"),
    col("valeur_benchmark", "Valeur benchmark", "Benchmark value"),
    col("port_reference", "Port reference", "Reference port"),
    col("source", "Source", "Source"),
    col("ecart_pct", "Ecart %", "Gap %"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("indicateur", "Indicateur", "Indicator"),
    num("valeur_interne", "Valeur interne", "Internal value"),
    num("valeur_benchmark", "Valeur benchmark", "Benchmark value"),
    txt("port_reference", "Port reference", "Reference port"),
    txt("source", "Source", "Source"),
    num("ecart_pct", "Ecart %", "Gap %"),
  ],
};


export const registrePredictiveModel: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "predictive_analytics",
  tcode: "registre-predictive-analytics",
  icon: Icons.Brain,
  titre: "Analyses predictives",
  titreEn: "Predictive analytics",
  description: "Modeles ML simples (regression, serie temporelle).",
  descriptionEn: "Simple ML (regression, time series).",
  aide: "Score de precision affiche sur chaque prediction.",
  aideEn: "Precision displayed per prediction.",
  lister: (params) => api.lister("predictive-models", params),
  creer: (data) => api.creer("predictive-models", data),
  modifier: (id, data) => api.modifier("predictive-models", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom_modele", "Nom modele", "Model name"),
    col("type_modele", "Type", "Type"),
    col("variable_predite", "Variable predite", "Target variable"),
    col("precision_pct", "Precision %", "Precision %"),
    col("date_entrainement", "Entrainement", "Training date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom_modele", "Nom modele", "Model name"),
    sel("type_modele", "Type", "Type", "type_modele"),
    txt("variable_predite", "Variable predite", "Target variable"),
    num("precision_pct", "Precision %", "Precision %"),
    dtx("date_entrainement", "Entrainement", "Training date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreCustomDashboard: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "custom_dashboard",
  tcode: "registre-custom-dashboards",
  icon: Icons.LayoutDashboard,
  titre: "Tableaux de bord personnalises",
  titreEn: "Custom dashboards",
  description: "Dashboards configures par utilisateur.",
  descriptionEn: "User-configured dashboards.",
  aide: "Partage possible en lecture seule.",
  aideEn: "Shareable in read-only.",
  lister: (params) => api.lister("custom-dashboards", params),
  creer: (data) => api.creer("custom-dashboards", data),
  modifier: (id, data) => api.modifier("custom-dashboards", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom", "Nom", "Name"),
    col("proprietaire", "Proprietaire", "Owner"),
    col("nb_widgets", "Nb widgets", "Widgets"),
    col("partage", "Partage", "Sharing"),
    col("frequence", "Frequence", "Frequency"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("proprietaire", "Proprietaire", "Owner"),
    num("nb_widgets", "Nb widgets", "Widgets"),
    sel("partage", "Partage", "Sharing", "partage"),
    sel("frequence", "Frequence", "Frequency", "frequence"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registreReportExport: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "export_reports",
  tcode: "registre-export-reports",
  icon: Icons.Send,
  titre: "Exports planifies / abonnes",
  titreEn: "Scheduled / subscribed exports",
  description: "Envois automatiques de rapports.",
  descriptionEn: "Automatic report delivery.",
  aide: "Format PDF / XLSX / CSV.",
  aideEn: "PDF / XLSX / CSV.",
  lister: (params) => api.lister("report-exports", params),
  creer: (data) => api.creer("report-exports", data),
  modifier: (id, data) => api.modifier("report-exports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("rapport_source", "Rapport source", "Source report"),
    col("format", "Format", "Format"),
    col("frequence", "Frequence", "Frequency"),
    col("destinataires", "Destinataires", "Recipients"),
    col("dernier_envoi", "Dernier envoi", "Last send"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("rapport_source", "Rapport source", "Source report"),
    sel("format", "Format", "Format", "format"),
    sel("frequence", "Frequence", "Frequency", "frequence"),
    txt("destinataires", "Destinataires", "Recipients"),
    dtx("dernier_envoi", "Dernier envoi", "Last send"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreKpiDefinition: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "kpi_definition",
  tcode: "registre-kpi-definitions",
  icon: Icons.BookMarked,
  titre: "Catalogue et definitions KPI",
  titreEn: "KPI catalog and definitions",
  description: "Formule, unite, source, proprietaire.",
  descriptionEn: "Formula, unit, source, owner.",
  aide: "Revue annuelle obligatoire.",
  aideEn: "Annual review mandatory.",
  lister: (params) => api.lister("kpi-definitions", params),
  creer: (data) => api.creer("kpi-definitions", data),
  modifier: (id, data) => api.modifier("kpi-definitions", id, data),
  unicite: "code_kpi",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_kpi", "Code KPI", "KPI code"),
    col("intitule", "Intitule", "Title"),
    col("formule", "Formule", "Formula"),
    col("unite", "Unite", "Unit"),
    col("source", "Source", "Source"),
    col("periodicite", "Periodicite", "Frequency"),
    col("responsable", "Responsable", "Owner"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("code_kpi", "Code KPI", "KPI code", { requisCreation: true }),
    txt("intitule", "Intitule", "Title"),
    txt("formule", "Formule", "Formula"),
    txt("unite", "Unite", "Unit"),
    txt("source", "Source", "Source"),
    sel("periodicite", "Periodicite", "Frequency", "periodicite"),
    txt("responsable", "Responsable", "Owner"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registreDrillPath: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "drill_down",
  tcode: "registre-drill-down-analytics",
  icon: Icons.Layers,
  titre: "Explorations en cascade",
  titreEn: "Drill-down analytics",
  description: "Chemins d'exploration definis.",
  descriptionEn: "Defined exploration paths.",
  aide: "Rebond possible entre modules.",
  aideEn: "Cross-module jump allowed.",
  lister: (params) => api.lister("drill-paths", params),
  creer: (data) => api.creer("drill-paths", data),
  modifier: (id, data) => api.modifier("drill-paths", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom", "Nom", "Name"),
    col("niveau_1", "Niveau 1", "Level 1"),
    col("niveau_2", "Niveau 2", "Level 2"),
    col("niveau_3", "Niveau 3", "Level 3"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("niveau_1", "Niveau 1", "Level 1"),
    txt("niveau_2", "Niveau 2", "Level 2"),
    txt("niveau_3", "Niveau 3", "Level 3"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registreCohortAnalysis: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "cohort_analysis",
  tcode: "registre-cohort-analysis",
  icon: Icons.Users,
  titre: "Analyse de cohortes",
  titreEn: "Cohort analysis",
  description: "Groupements clients par date ou segment.",
  descriptionEn: "Client grouping by date or segment.",
  aide: "Suivi retention 12 mois.",
  aideEn: "12-month retention tracking.",
  lister: (params) => api.lister("cohort-analyses", params),
  creer: (data) => api.creer("cohort-analyses", data),
  modifier: (id, data) => api.modifier("cohort-analyses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom_cohorte", "Nom cohort", "Cohort name"),
    col("criteres", "Criteres", "Criteria"),
    col("taille", "Taille", "Size"),
    col("date_debut", "Debut", "Start"),
    col("taux_retention_m1_pct", "Retention M1 %", "M1 retention %"),
    col("taux_retention_m12_pct", "Retention M12 %", "M12 retention %"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom_cohorte", "Nom cohort", "Cohort name"),
    txt("criteres", "Criteres", "Criteria"),
    num("taille", "Taille", "Size"),
    dt("date_debut", "Debut", "Start"),
    num("taux_retention_m1_pct", "Retention M1 %", "M1 retention %"),
    num("taux_retention_m12_pct", "Retention M12 %", "M12 retention %"),
  ],
};


export const registreAnomalyRecord: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "anomaly_detection",
  tcode: "registre-anomaly-detection",
  icon: Icons.AlertTriangle,
  titre: "Detection anomalies / seuils",
  titreEn: "Anomaly detection / thresholds",
  description: "Signaux d'alerte automatiques.",
  descriptionEn: "Automatic alert signals.",
  aide: "Revue hebdomadaire DAF.",
  aideEn: "Weekly CFO review.",
  lister: (params) => api.lister("anomaly-records", params),
  creer: (data) => api.creer("anomaly-records", data),
  modifier: (id, data) => api.modifier("anomaly-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("indicateur", "Indicateur", "Indicator"),
    col("valeur_constatee", "Valeur constatee", "Observed value"),
    col("valeur_attendue", "Valeur attendue", "Expected value"),
    col("seuil_pct", "Seuil %", "Threshold %"),
    col("date_detection", "Date detection", "Detection date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("indicateur", "Indicateur", "Indicator"),
    num("valeur_constatee", "Valeur constatee", "Observed value"),
    num("valeur_attendue", "Valeur attendue", "Expected value"),
    num("seuil_pct", "Seuil %", "Threshold %"),
    dtx("date_detection", "Date detection", "Detection date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreRegulatoryReport: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "regulatory_report",
  tcode: "registre-regulatory-reports",
  icon: Icons.FileText,
  titre: "Rapports reglementaires (APN, douane)",
  titreEn: "Regulatory reports (CPA, customs)",
  description: "Declarations obligatoires.",
  descriptionEn: "Mandatory filings.",
  aide: "Depot dans le delai legal.",
  aideEn: "Filed within legal deadline.",
  lister: (params) => api.lister("regulatory-reports", params),
  creer: (data) => api.creer("regulatory-reports", data),
  modifier: (id, data) => api.modifier("regulatory-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("autorite", "Autorite", "Authority"),
    col("type_rapport", "Type rapport", "Report type"),
    col("periode_debut", "Debut", "Start"),
    col("periode_fin", "Fin", "End"),
    col("date_depot", "Depot", "Filing date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("autorite", "Autorite", "Authority"),
    sel("type_rapport", "Type rapport", "Report type", "type_rapport"),
    dt("periode_debut", "Debut", "Start"),
    dt("periode_fin", "Fin", "End"),
    dt("date_depot", "Depot", "Filing date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};

