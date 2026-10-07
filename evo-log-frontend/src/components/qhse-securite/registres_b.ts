/**
 * Configs Registre pour qhse-securite (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("qhse-securite");

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

export const registreQhseNearMiss: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "near_miss",
  tcode: "registre-near-miss-reports",
  icon: Icons.TriangleAlert,
  titre: "Quasi-accidents (situations dangereuses)",
  titreEn: "Near-miss reports",
  description: "Declaration des situations dangereuses sans accident.",
  descriptionEn: "Reporting of hazardous situations without accident.",
  aide: "Alimente l analyse preventive.",
  aideEn: "Feeds preventive analysis.",
  lister: (params) => api.lister("qhseb-near-misses", params),
  creer: (data) => api.creer("qhseb-near-misses", data),
  modifier: (id, data) => api.modifier("qhseb-near-misses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference declaration", "Report reference"),
    col("site", "Site", "Site"),
    col("date_evenement", "Date evenement", "Event date"),
    col("zone", "Zone", "Area"),
    col("description", "Description", "Description"),
    col("gravite_potentielle", "Gravite potentielle", "Potential severity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference declaration", "Report reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    dtx("date_evenement", "Date evenement", "Event date"),
    txt("zone", "Zone", "Area"),
    txt("description", "Description", "Description"),
    txt("gravite_potentielle", "Gravite potentielle", "Potential severity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQhseCalibration: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "calibration",
  tcode: "registre-calibration-records",
  icon: Icons.Gauge,
  titre: "Etalonnage instruments de mesure",
  titreEn: "Instrument calibration",
  description: "Traacabilite de l etalonnage des instruments de mesure.",
  descriptionEn: "Traceability of measuring instrument calibration.",
  aide: "Instrument hors etalonnage = mesure non fiable.",
  aideEn: "Uncalibrated = unreliable reading.",
  lister: (params) => api.lister("qhseb-calibrations", params),
  creer: (data) => api.creer("qhseb-calibrations", data),
  modifier: (id, data) => api.modifier("qhseb-calibrations", id, data),
  unicite: "numero_instrument",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_instrument", "Numero instrument", "Instrument number"),
    col("designation", "Designation", "Designation"),
    col("service", "Service", "Department"),
    col("date_etallonage", "Date etalonnage", "Calibration date"),
    col("date_prochaine", "Prochain etalonnage", "Next calibration"),
    col("ecart_constate", "Ecart constate", "Observed deviation"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_instrument", "Numero instrument", "Instrument number", { requisCreation: true }),
    txt("designation", "Designation", "Designation"),
    txt("service", "Service", "Department"),
    dt("date_etallonage", "Date etalonnage", "Calibration date"),
    dt("date_prochaine", "Prochain etalonnage", "Next calibration"),
    num("ecart_constate", "Ecart constate", "Observed deviation"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQhseWasteManifest: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "waste_manifest",
  tcode: "registre-waste-manifests",
  icon: Icons.FileStack,
  titre: "Bordereaux de suivi des dechets (BSD)",
  titreEn: "Waste transfer notes",
  description: "Bordereaux de suivi et tracabilite des dechets.",
  descriptionEn: "Waste tracking and traceability notes.",
  aide: "Obligatoire pour dechets dangereux.",
  aideEn: "Mandatory for hazardous waste.",
  lister: (params) => api.lister("qhseb-waste-manifests", params),
  creer: (data) => api.creer("qhseb-waste-manifests", data),
  modifier: (id, data) => api.modifier("qhseb-waste-manifests", id, data),
  unicite: "numero_bsd",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_bsd", "Numero BSD", "Waste note number"),
    col("site", "Site", "Site"),
    col("type_dechet", "Type dechet", "Waste type"),
    col("dangerosite", "Dangerosite", "Hazard class"),
    col("quantite_tonnes", "Quantite (t)", "Quantity (t)"),
    col("destination", "Destination", "Destination"),
    col("date_enlevement", "Date enlevement", "Collection date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_bsd", "Numero BSD", "Waste note number", { requisCreation: true }),
    txt("site", "Site", "Site"),
    txt("type_dechet", "Type dechet", "Waste type"),
    txt("dangerosite", "Dangerosite", "Hazard class"),
    num("quantite_tonnes", "Quantite (t)", "Quantity (t)"),
    txt("destination", "Destination", "Destination"),
    dt("date_enlevement", "Date enlevement", "Collection date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQhseTrainingRecord: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "training_record",
  tcode: "registre-training-records",
  icon: Icons.GraduationCap,
  titre: "Habilitations et formations securite",
  titreEn: "Safety training records",
  description: "Suivi des habilitations et formations securite du personnel.",
  descriptionEn: "Tracking of staff safety qualifications and training.",
  aide: "Habilitation expiree = poste non couvert.",
  aideEn: "Expired cert = uncovered post.",
  lister: (params) => api.lister("qhseb-training-records", params),
  creer: (data) => api.creer("qhseb-training-records", data),
  modifier: (id, data) => api.modifier("qhseb-training-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("type_habilitation", "Type habilitation", "Qualification type"),
    col("date_formation", "Date formation", "Training date"),
    col("date_validite", "Date validite", "Validity date"),
    col("formateur", "Formateur", "Trainer"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("type_habilitation", "Type habilitation", "Qualification type"),
    dt("date_formation", "Date formation", "Training date"),
    dt("date_validite", "Date validite", "Validity date"),
    txt("formateur", "Formateur", "Trainer"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQhseWorkPermit: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "work_permit",
  tcode: "registre-work-permits",
  icon: Icons.ShieldCheck,
  titre: "Permis de travail (PTW)",
  titreEn: "Permits to work",
  description: "Autorisations formelles pour travaux a risque.",
  descriptionEn: "Formal authorizations for high-risk work.",
  aide: "Consignation et surveillance obligatoires.",
  aideEn: "Lockout and supervision mandatory.",
  lister: (params) => api.lister("qhseb-work-permits", params),
  creer: (data) => api.creer("qhseb-work-permits", data),
  modifier: (id, data) => api.modifier("qhseb-work-permits", id, data),
  unicite: "numero_ptw",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_ptw", "Numero PTW", "Permit number"),
    col("site", "Site", "Site"),
    col("type_travaux", "Type travaux", "Work type"),
    col("zone_travail", "Zone de travail", "Work area"),
    col("demandeur", "Demandeur", "Requester"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_ptw", "Numero PTW", "Permit number", { requisCreation: true }),
    txt("site", "Site", "Site"),
    txt("type_travaux", "Type travaux", "Work type"),
    txt("zone_travail", "Zone de travail", "Work area"),
    txt("demandeur", "Demandeur", "Requester"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};

