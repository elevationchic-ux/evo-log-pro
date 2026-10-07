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

export const registreRptcScheduledReport: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "scheduled_report",
  tcode: "registre-scheduled-reports",
  icon: Icons.CalendarClock,
  titre: "Rapports planifies",
  titreEn: "Scheduled reports",
  description: "Execution periodique automatique d' un rapport.",
  descriptionEn: "Automatic periodic run of a report.",
  aide: "Frequence et destinataires parametrent l' envoi.",
  aideEn: "Frequency and recipients drive delivery.",
  lister: (params) => api.lister("rptc-scheduled-reports", params),
  creer: (data) => api.creer("rptc-scheduled-reports", data),
  modifier: (id, data) => api.modifier("rptc-scheduled-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference rapport", "Report reference"),
    col("nom", "Nom", "Name"),
    col("frequence", "Frequence", "Frequency"),
    col("format", "Format", "Format"),
    col("destinataires", "Destinataires", "Recipients"),
    col("prochaine_execution", "Prochaine execution", "Next run"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference rapport", "Report reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("frequence", "Frequence", "Frequency"),
    txt("format", "Format", "Format"),
    txt("destinataires", "Destinataires", "Recipients"),
    dtx("prochaine_execution", "Prochaine execution", "Next run"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRptcReportTemplate: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "report_template",
  tcode: "registre-report-templates",
  icon: Icons.LayoutTemplate,
  titre: "Modeles de rapport",
  titreEn: "Report templates",
  description: "Definition reutilisable de la mise en page d' un rapport.",
  descriptionEn: "Reusable definition of a report layout.",
  aide: "Versionne le modele ; les rapports s' y referent.",
  aideEn: "Versioned model; reports reference it.",
  lister: (params) => api.lister("rptc-report-templates", params),
  creer: (data) => api.creer("rptc-report-templates", data),
  modifier: (id, data) => api.modifier("rptc-report-templates", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference modele", "Template reference"),
    col("nom", "Nom", "Name"),
    col("categorie", "Categorie", "Category"),
    col("source_donnees", "Source de donnees", "Data source"),
    col("version", "Version", "Version"),
    col("nb_blocs", "Nombre de blocs", "Block count"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference modele", "Template reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("categorie", "Categorie", "Category"),
    txt("source_donnees", "Source de donnees", "Data source"),
    txt("version", "Version", "Version"),
    num("nb_blocs", "Nombre de blocs", "Block count"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRptcDataExport: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "data_export",
  tcode: "registre-data-exports",
  icon: Icons.Download,
  titre: "Extractions de donnees",
  titreEn: "Data exports",
  description: "Demande d' extraction d' un jeu de donnees au format fichier.",
  descriptionEn: "Request to extract a dataset into a file.",
  aide: "Tracabilite : qui, quand, quel volume exporte.",
  aideEn: "Traceability: who, when, how many rows exported.",
  lister: (params) => api.lister("rptc-data-exports", params),
  creer: (data) => api.creer("rptc-data-exports", data),
  modifier: (id, data) => api.modifier("rptc-data-exports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference extraction", "Export reference"),
    col("libelle", "Libelle", "Label"),
    col("module_source", "Module source", "Source module"),
    col("format", "Format", "Format"),
    col("filtres", "Filtres", "Filters"),
    col("lignes_exportees", "Lignes exportees", "Rows exported"),
    col("demandeur", "Demandeur", "Requester"),
    col("date_export", "Date export", "Export date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference extraction", "Export reference", { requisCreation: true }),
    txt("libelle", "Libelle", "Label"),
    txt("module_source", "Module source", "Source module"),
    txt("format", "Format", "Format"),
    txt("filtres", "Filtres", "Filters"),
    num("lignes_exportees", "Lignes exportees", "Rows exported"),
    txt("demandeur", "Demandeur", "Requester"),
    dtx("date_export", "Date export", "Export date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRptcAdHocQuery: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "ad_hoc_query",
  tcode: "registre-ad-hoc-queries",
  icon: Icons.Terminal,
  titre: "Requetes ad hoc",
  titreEn: "Ad-hoc queries",
  description: "Requete analytique ponctuelle construite par un utilisateur.",
  descriptionEn: "One-off analytical query built by a user.",
  aide: "Une requete est partageable et versionnee.",
  aideEn: "A query can be shared and versioned.",
  lister: (params) => api.lister("rptc-ad-hoc-queries", params),
  creer: (data) => api.creer("rptc-ad-hoc-queries", data),
  modifier: (id, data) => api.modifier("rptc-ad-hoc-queries", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference requete", "Query reference"),
    col("titre", "Titre", "Title"),
    col("source_donnees", "Source de donnees", "Data source"),
    col("dimensions", "Dimensions", "Dimensions"),
    col("auteur", "Auteur", "Author"),
    col("derniere_execution", "Derniere execution", "Last run"),
    col("partage", "Partagee", "Shared"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference requete", "Query reference", { requisCreation: true }),
    txt("titre", "Titre", "Title"),
    txt("source_donnees", "Source de donnees", "Data source"),
    txt("dimensions", "Dimensions", "Dimensions"),
    txt("auteur", "Auteur", "Author"),
    dtx("derniere_execution", "Derniere execution", "Last run"),
    chk("partage", "Partagee", "Shared"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRptcOlapCube: ConfigRegistre = {
  permModule: "reports",
  permSousModule: "olap_cube",
  tcode: "registre-olap-cubes",
  icon: Icons.Database,
  titre: "Cubes analytiques",
  titreEn: "OLAP cubes",
  description: "Cube multidimensionnel prepoure pour l' analyse.",
  descriptionEn: "Pre-computed multidimensional cube for analysis.",
  aide: "Dimensions et mesures definissent les coupes disponibles.",
  aideEn: "Dimensions and measures define available cuts.",
  lister: (params) => api.lister("rptc-olap-cubes", params),
  creer: (data) => api.creer("rptc-olap-cubes", data),
  modifier: (id, data) => api.modifier("rptc-olap-cubes", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference cube", "Cube reference"),
    col("nom", "Nom", "Name"),
    col("source", "Source", "Source"),
    col("dimensions", "Dimensions", "Dimensions"),
    col("mesures", "Mesures", "Measures"),
    col("nb_lignes", "Nombre de lignes", "Row count"),
    col("date_dernier_refresh", "Dernier refresh", "Last refresh"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference cube", "Cube reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("source", "Source", "Source"),
    txt("dimensions", "Dimensions", "Dimensions"),
    txt("mesures", "Mesures", "Measures"),
    num("nb_lignes", "Nombre de lignes", "Row count"),
    dtx("date_dernier_refresh", "Dernier refresh", "Last refresh"),
    txt("statut", "Statut", "Status"),
  ],
};

