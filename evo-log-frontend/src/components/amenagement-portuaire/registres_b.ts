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

export const registreAmgtbDredgingProject: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "dredging_project",
  tcode: "registre-dredging-projects",
  icon: Icons.Shovel,
  titre: "Projets de dragage",
  titreEn: "Dredging projects",
  description: "Suivi des campagnes de dragage des chenaux et zones d'accostage.",
  descriptionEn: "Tracking of channel and berth basin dredging campaigns.",
  aide: "Volume rejete vs volume dragre ; exutoire delimite.",
  aideEn: "Spoil volume vs dredged volume; defined disposal site.",
  lister: (params) => api.lister("amgtb-dredging-projects", params),
  creer: (data) => api.creer("amgtb-dredging-projects", data),
  modifier: (id, data) => api.modifier("amgtb-dredging-projects", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference projet", "Project reference"),
    col("zone", "Zone", "Area"),
    col("objectif_tirant_eau_m", "Objectif tirant d'eau (m)", "Target draft (m)"),
    col("volume_a_draguer_m3", "Volume a draguer (m3)", "Volume to dredge (m3)"),
    col("volume_rejete_m3", "Volume rejete (m3)", "Spoil volume (m3)"),
    col("entreprise", "Entreprise", "Contractor"),
    col("date_debut", "Date debut", "Start date"),
    col("date_fin", "Date fin", "End date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference projet", "Project reference", { requisCreation: true }),
    txt("zone", "Zone", "Area"),
    num("objectif_tirant_eau_m", "Objectif tirant d'eau (m)", "Target draft (m)"),
    num("volume_a_draguer_m3", "Volume a draguer (m3)", "Volume to dredge (m3)"),
    num("volume_rejete_m3", "Volume rejete (m3)", "Spoil volume (m3)"),
    txt("entreprise", "Entreprise", "Contractor"),
    dt("date_debut", "Date debut", "Start date"),
    dt("date_fin", "Date fin", "End date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAmgtbConcessionPlot: ConfigRegistre = {
  permModule: "amenagement",
  permSousModule: "concession_plot",
  tcode: "registre-concession-plots",
  icon: Icons.LandPlot,
  titre: "Parcelles sous concession",
  titreEn: "Concession plots",
  description: "Inventaire des terrains portuaires concodes et de leur echeance.",
  descriptionEn: "Inventory of port land plots under concession and their expiry.",
  aide: "Redevance annuelle et echeance suivies par parcelle.",
  aideEn: "Annual fee and expiry tracked per plot.",
  lister: (params) => api.lister("amgtb-concession-plots", params),
  creer: (data) => api.creer("amgtb-concession-plots", data),
  modifier: (id, data) => api.modifier("amgtb-concession-plots", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference parcelle", "Plot reference"),
    col("designation", "Designation", "Designation"),
    col("superficie_m2", "Superficie (m2)", "Area (m2)"),
    col("concessionnaire", "Concessionnaire", "Concessionaire"),
    col("date_debut", "Debut concession", "Concession start"),
    col("date_echeance", "Echeance", "Expiry date"),
    col("redevance_annuelle", "Redevance annuelle", "Annual fee"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference parcelle", "Plot reference", { requisCreation: true }),
    txt("designation", "Designation", "Designation"),
    num("superficie_m2", "Superficie (m2)", "Area (m2)"),
    txt("concessionnaire", "Concessionnaire", "Concessionaire"),
    dt("date_debut", "Debut concession", "Concession start"),
    dt("date_echeance", "Echeance", "Expiry date"),
    num("redevance_annuelle", "Redevance annuelle", "Annual fee"),
    txt("statut", "Statut", "Status"),
  ],
};

