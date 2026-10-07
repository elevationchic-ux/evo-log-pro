/**
 * Configs Registre pour amenagement-portuaire (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("amenagement-portuaire");

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

export const registreConstructionProgress: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "construction_tracking",
  tcode: "registre-construction-tracking",
  icon: Icons.Building2,
  titre: "Suivi avancement physique travaux",
  titreEn: "Physical construction progress",
  description: "Pourcentages d'avancement par lot.",
  descriptionEn: "Progress % per lot.",
  aide: "Photo obligatoire a chaque mise a jour.",
  aideEn: "Photo required at each update.",
  lister: (params) => api.lister("construction-progresses", params),
  creer: (data) => api.creer("construction-progresses", data),
  modifier: (id, data) => api.modifier("construction-progresses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("marche_id", "Marche", "Contract"),
    col("lot", "Lot", "Lot"),
    col("avancement_pct", "Avancement %", "Progress %"),
    col("date_releve", "Releve", "Observation date"),
    col("surface_m2", "Surface m2", "Surface m2"),
    col("observateur", "Observateur", "Observer"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("marche_id", "Marche", "Contract"),
    txt("lot", "Lot", "Lot"),
    num("avancement_pct", "Avancement %", "Progress %"),
    dt("date_releve", "Releve", "Observation date"),
    num("surface_m2", "Surface m2", "Surface m2"),
    txt("observateur", "Observateur", "Observer"),
  ],
};


export const registreInfrastructureMaintenance: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "infrastructure_maintenance",
  tcode: "registre-infrastructure-maintenance",
  icon: Icons.Wrench,
  titre: "Maintenance preventive ouvrages",
  titreEn: "Preventive infrastructure maintenance",
  description: "Plan de maintenance des ouvrages.",
  descriptionEn: "Maintenance plan for structures.",
  aide: "Conforme aux regles portuaires.",
  aideEn: "Compliant with port rules.",
  lister: (params) => api.lister("infrastructure-maintenances", params),
  creer: (data) => api.creer("infrastructure-maintenances", data),
  modifier: (id, data) => api.modifier("infrastructure-maintenances", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ouvrage_id", "Ouvrage", "Structure"),
    col("type_intervention", "Type intervention", "Intervention type"),
    col("frequence_mois", "Frequence (mois)", "Frequency (months)"),
    col("date_prochaine", "Prochaine", "Next"),
    col("cout_estime_xaf", "Cout estime", "Estimated cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("ouvrage_id", "Ouvrage", "Structure"),
    sel("type_intervention", "Type intervention", "Intervention type", "type_intervention"),
    num("frequence_mois", "Frequence (mois)", "Frequency (months)"),
    dt("date_prochaine", "Prochaine", "Next"),
    num("cout_estime_xaf", "Cout estime", "Estimated cost"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreIspsRecord: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "port_security_isps",
  tcode: "registre-port-security-isps",
  icon: Icons.ShieldAlert,
  titre: "Surete ISPS (distinct QHSE)",
  titreEn: "ISPS security (distinct from QHSE)",
  description: "Niveaux de surete, exercices ISPS.",
  descriptionEn: "Security levels, ISPS drills.",
  aide: "PV obligatoire.",
  aideEn: "Mandatory minutes.",
  lister: (params) => api.lister("isps-records", params),
  creer: (data) => api.creer("isps-records", data),
  modifier: (id, data) => api.modifier("isps-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("niveau_isps", "Niveau ISPS", "ISPS level"),
    col("date_application", "Application", "Applied date"),
    col("motif", "Motif", "Reason"),
    col("authorite_emetteuse", "Autorite emetteuse", "Issuing authority"),
    col("date_levee", "Levee", "Lift date"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    sel("niveau_isps", "Niveau ISPS", "ISPS level", "niveau_isps"),
    dtx("date_application", "Application", "Applied date"),
    txt("motif", "Motif", "Reason"),
    txt("authorite_emetteuse", "Autorite emetteuse", "Issuing authority"),
    dtx("date_levee", "Levee", "Lift date"),
  ],
};


export const registrePortPerception: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "port_pricing",
  tcode: "registre-port-pricing",
  icon: Icons.Calculator,
  titre: "Redevances et perceptions portuaires",
  titreEn: "Port fees and perceptions",
  description: "Grille tarifaire du domaine portuaire.",
  descriptionEn: "Port fee grid.",
  aide: "Validee par arrete ministeriel.",
  aideEn: "Approved by ministerial decree.",
  lister: (params) => api.lister("port-perceptions", params),
  creer: (data) => api.creer("port-perceptions", data),
  modifier: (id, data) => api.modifier("port-perceptions", id, data),
  unicite: "code_perception",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_perception", "Code", "Code"),
    col("intitule", "Intitule", "Title"),
    col("type_perception", "Type", "Type"),
    col("base_calcul", "Base calcul", "Calculation base"),
    col("tarif_xaf", "Tarif XAF", "Fee XAF"),
    col("unite", "Unite", "Unit"),
    col("arrete_reference", "Arrete", "Decree ref"),
    col("date_application", "Application", "Application date"),
  ],
  champs: [
    txt("code_perception", "Code", "Code", { requisCreation: true }),
    txt("intitule", "Intitule", "Title"),
    sel("type_perception", "Type", "Type", "type_perception"),
    txt("base_calcul", "Base calcul", "Calculation base"),
    num("tarif_xaf", "Tarif XAF", "Fee XAF"),
    txt("unite", "Unite", "Unit"),
    txt("arrete_reference", "Arrete", "Decree ref"),
    dt("date_application", "Application", "Application date"),
  ],
};


export const registreAnnualActivityReport: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "activity_report",
  tcode: "registre-activity-report",
  icon: Icons.FileBarChart2,
  titre: "Rapport d'activite annuel",
  titreEn: "Annual activity report",
  description: "Bilan annuel portuaire.",
  descriptionEn: "Annual port summary.",
  aide: "Approuve par conseil d'administration.",
  aideEn: "Board approved.",
  lister: (params) => api.lister("annual-activity-reports", params),
  creer: (data) => api.creer("annual-activity-reports", data),
  modifier: (id, data) => api.modifier("annual-activity-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("annee", "Annee", "Year"),
    col("tonnage_traite_t", "Tonnage traite (t)", "Tonnage handled (t)"),
    col("nb_escales", "Nb escales", "Call count"),
    col("nb_conteneurs_evp", "EVP", "TEU"),
    col("recettes_xaf", "Recettes XAF", "Revenue XAF"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("annee", "Annee", "Year"),
    num("tonnage_traite_t", "Tonnage traite (t)", "Tonnage handled (t)"),
    num("nb_escales", "Nb escales", "Call count"),
    num("nb_conteneurs_evp", "EVP", "TEU"),
    num("recettes_xaf", "Recettes XAF", "Revenue XAF"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSigLayer: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "domain_cartography",
  tcode: "registre-domain-cartography",
  icon: Icons.Map,
  titre: "SIG / cartographie domaine",
  titreEn: "Port GIS / cartography",
  description: "Couches SIG du domaine.",
  descriptionEn: "Port GIS layers.",
  aide: "Refonte tous les 5 ans.",
  aideEn: "Refresh every 5 years.",
  lister: (params) => api.lister("sig-layers", params),
  creer: (data) => api.creer("sig-layers", data),
  modifier: (id, data) => api.modifier("sig-layers", id, data),
  unicite: "code_couche",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_couche", "Code couche", "Layer code"),
    col("nom", "Nom", "Name"),
    col("type_couche", "Type couche", "Layer type"),
    col("projection", "Projection", "Projection"),
    col("date_maj", "Derniere MAJ", "Last update"),
    col("superficie_ha", "Superficie (ha)", "Area (ha)"),
  ],
  champs: [
    txt("code_couche", "Code couche", "Layer code", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    sel("type_couche", "Type couche", "Layer type", "type_couche"),
    txt("projection", "Projection", "Projection"),
    dt("date_maj", "Derniere MAJ", "Last update"),
    num("superficie_ha", "Superficie (ha)", "Area (ha)"),
  ],
};


export const registreDomainArchive: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "archive_management",
  tcode: "registre-archive-management",
  icon: Icons.Archive,
  titre: "Archivage pieces domaniales",
  titreEn: "Domain paper archive",
  description: "Inventaire archives domaniales.",
  descriptionEn: "Domain archive inventory.",
  aide: "Duree conservation reglementaire.",
  aideEn: "Regulatory retention period.",
  lister: (params) => api.lister("domain-archives", params),
  creer: (data) => api.creer("domain-archives", data),
  modifier: (id, data) => api.modifier("domain-archives", id, data),
  unicite: "cote_archive",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("cote_archive", "Cote archive", "Archive ref"),
    col("titre", "Titre", "Title"),
    col("type_piece", "Type piece", "Document type"),
    col("periode_couverte", "Periode", "Period covered"),
    col("localisation", "Localisation", "Location"),
    col("duree_conservation_an", "Duree conservation (an)", "Retention (y)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("cote_archive", "Cote archive", "Archive ref", { requisCreation: true }),
    txt("titre", "Titre", "Title"),
    sel("type_piece", "Type piece", "Document type", "type_piece"),
    txt("periode_couverte", "Periode", "Period covered"),
    txt("localisation", "Localisation", "Location"),
    num("duree_conservation_an", "Duree conservation (an)", "Retention (y)"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreAmenagementKpi: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "development_kpi",
  tcode: "registre-development-kpi",
  icon: Icons.Gauge,
  titre: "Tableau bord indicateurs amenagement",
  titreEn: "Amenagement KPI dashboard",
  description: "Suivi des indicateurs amenagement.",
  descriptionEn: "Track development KPIs.",
  aide: "Revue trimestrielle direction technique.",
  aideEn: "Quarterly review.",
  lister: (params) => api.lister("amenagement-kpis", params),
  creer: (data) => api.creer("amenagement-kpis", data),
  modifier: (id, data) => api.modifier("amenagement-kpis", id, data),
  unicite: "code_kpi",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_kpi", "Code KPI", "KPI code"),
    col("intitule", "Intitule", "Title"),
    col("periode", "Periode", "Period"),
    col("valeur", "Valeur", "Value"),
    col("objectif", "Objectif", "Target"),
    col("ecart_pct", "Ecart %", "Gap %"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_kpi", "Code KPI", "KPI code", { requisCreation: true }),
    txt("intitule", "Intitule", "Title"),
    txt("periode", "Periode", "Period"),
    num("valeur", "Valeur", "Value"),
    num("objectif", "Objectif", "Target"),
    num("ecart_pct", "Ecart %", "Gap %"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};

