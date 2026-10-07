/**
 * Configs Registre pour dashboard (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("dashboard");

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

export const registreDashboardbOperationalKpi: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "operational_kpi",
  tcode: "registre-operational-kpis",
  icon: Icons.Gauge,
  titre: "Indicateurs de performance operationnelle",
  titreEn: "Operational KPIs",
  description: "Valeur mesuree d'un indicateur pour une periode donnee.",
  descriptionEn: "Measured value of an indicator for a given period.",
  aide: "La valeur est confrontee a l'objectif et au seuil d'alerte.",
  aideEn: "Value is compared to target and alert threshold.",
  lister: (params) => api.lister("dashb-operational-kpis", params),
  creer: (data) => api.creer("dashb-operational-kpis", data),
  modifier: (id, data) => api.modifier("dashb-operational-kpis", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference indicateur", "KPI reference"),
    col("libelle", "Libelle", "Label"),
    col("module_source", "Module source", "Source module"),
    col("valeur", "Valeur", "Value"),
    col("unite", "Unite", "Unit"),
    col("periode", "Periode", "Period"),
    col("objectif", "Objectif", "Target"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference indicateur", "KPI reference", { requisCreation: true }),
    txt("libelle", "Libelle", "Label"),
    txt("module_source", "Module source", "Source module"),
    num("valeur", "Valeur", "Value"),
    txt("unite", "Unite", "Unit"),
    dt("periode", "Periode", "Period"),
    num("objectif", "Objectif", "Target"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDashboardbScorecard: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "scorecard",
  tcode: "registre-executive-scorecards",
  icon: Icons.Trophy,
  titre: "Tableaux de bord direction",
  titreEn: "Executive scorecards",
  description: "Synthese periodique des indicateurs d'une direction.",
  descriptionEn: "Periodic roll-up of a department's indicators.",
  aide: "Le score global agrege les indicateurs follows.",
  aideEn: "Global score aggregates the tracked indicators.",
  lister: (params) => api.lister("dashb-executive-scorecards", params),
  creer: (data) => api.creer("dashb-executive-scorecards", data),
  modifier: (id, data) => api.modifier("dashb-executive-scorecards", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference tableau", "Scorecard reference"),
    col("direction", "Direction", "Department"),
    col("periode", "Periode", "Period"),
    col("score_global", "Score global", "Global score"),
    col("nb_indicateurs", "Nombre d'indicateurs", "Indicator count"),
    col("tendance", "Tendance", "Trend"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference tableau", "Scorecard reference", { requisCreation: true }),
    txt("direction", "Direction", "Department"),
    dt("periode", "Periode", "Period"),
    num("score_global", "Score global", "Global score"),
    num("nb_indicateurs", "Nombre d'indicateurs", "Indicator count"),
    txt("tendance", "Tendance", "Trend"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDashboardbAlertRule: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "alert_rule",
  tcode: "registre-alert-rules",
  icon: Icons.BellRing,
  titre: "Regles d'alerte",
  titreEn: "Alert rules",
  description: "Condition declenchant une notification sur un indicateur.",
  descriptionEn: "Condition triggering a notification on an indicator.",
  aide: "Regle = indicateur + operateur + seuil + destinataires.",
  aideEn: "Rule = indicator + operator + threshold + recipients.",
  lister: (params) => api.lister("dashb-alert-rules", params),
  creer: (data) => api.creer("dashb-alert-rules", data),
  modifier: (id, data) => api.modifier("dashb-alert-rules", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference regle", "Rule reference"),
    col("indicateur", "Indicateur", "Indicator"),
    col("condition", "Condition", "Condition"),
    col("seuil", "Seuil", "Threshold"),
    col("destinataires", "Destinataires", "Recipients"),
    col("canal", "Canal", "Channel"),
    col("actif", "Active", "Active"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference regle", "Rule reference", { requisCreation: true }),
    txt("indicateur", "Indicateur", "Indicator"),
    txt("condition", "Condition", "Condition"),
    num("seuil", "Seuil", "Threshold"),
    txt("destinataires", "Destinataires", "Recipients"),
    txt("canal", "Canal", "Channel"),
    chk("actif", "Active", "Active"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDashboardbRefreshJob: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "refresh_job",
  tcode: "registre-data-refresh-jobs",
  icon: Icons.RefreshCw,
  titre: "Taches de rafraichissement",
  titreEn: "Data refresh jobs",
  description: "Execution periodique du rafraichissement des donnees agrgees.",
  descriptionEn: "Periodic execution of aggregated-data refresh.",
  aide: "Duree et lignes traitees caracterisent la fraicheur.",
  aideEn: "Duration and rows processed characterize freshness.",
  lister: (params) => api.lister("dashb-data-refresh-jobs", params),
  creer: (data) => api.creer("dashb-data-refresh-jobs", data),
  modifier: (id, data) => api.modifier("dashb-data-refresh-jobs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference tache", "Job reference"),
    col("source", "Source", "Source"),
    col("frequence", "Frequence", "Frequency"),
    col("derniere_execution", "Derniere execution", "Last run"),
    col("duree_sec", "Duree (s)", "Duration (s)"),
    col("lignes_traitees", "Lignes traitees", "Rows processed"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference tache", "Job reference", { requisCreation: true }),
    txt("source", "Source", "Source"),
    txt("frequence", "Frequence", "Frequency"),
    dtx("derniere_execution", "Derniere execution", "Last run"),
    num("duree_sec", "Duree (s)", "Duration (s)"),
    num("lignes_traitees", "Lignes traitees", "Rows processed"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDashboardbSavedView: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "saved_view",
  tcode: "registre-saved-views",
  icon: Icons.Bookmark,
  titre: "Vues enregistrees",
  titreEn: "Saved views",
  description: "Sauvegarde d'un parametrage de visualisation (filtres + type).",
  descriptionEn: "Persistence of a visualization setup (filters + type).",
  aide: "Une vue est privee sauf partage explicite.",
  aideEn: "A view is private unless explicitly shared.",
  lister: (params) => api.lister("dashb-saved-views", params),
  creer: (data) => api.creer("dashb-saved-views", data),
  modifier: (id, data) => api.modifier("dashb-saved-views", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference vue", "View reference"),
    col("nom", "Nom", "Name"),
    col("owner", "Proprietaire", "Owner"),
    col("type_visuel", "Type visuel", "Visual type"),
    col("filtres", "Filtres", "Filters"),
    col("partage", "Partagee", "Shared"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference vue", "View reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("owner", "Proprietaire", "Owner"),
    txt("type_visuel", "Type visuel", "Visual type"),
    txt("filtres", "Filtres", "Filters"),
    chk("partage", "Partagee", "Shared"),
    txt("statut", "Statut", "Status"),
  ],
};

