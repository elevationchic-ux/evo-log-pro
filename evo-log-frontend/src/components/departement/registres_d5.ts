/**
 * Configs Registre pour departement (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("departement");

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

export const registreDepObjective: ConfigRegistre = {
  permModule: "departments",
  permSousModule: "objective",
  tcode: "registre-objectives",
  icon: Icons.Target,
  titre: "Objectifs de service",
  titreEn: "Department objectives",
  description: "Objectif de service suivi par le chef de departement.",
  descriptionEn: "Department objective tracked by the department head.",
  aide: "L' ecart entre cible et realise mesure l' atteinte.",
  aideEn: "Gap between target and actual measures attainment.",
  lister: (params) => api.lister("dep-objectives", params),
  creer: (data) => api.creer("dep-objectives", data),
  modifier: (id, data) => api.modifier("dep-objectives", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("libelle", "Libelle", "Label"),
    col("indicateur", "Indicateur", "Indicator"),
    col("cible", "Cible", "Target"),
    col("realise", "Realise", "Actual"),
    col("trimestre", "Trimestre", "Quarter"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("libelle", "Libelle", "Label"),
    txt("indicateur", "Indicateur", "Indicator"),
    num("cible", "Cible", "Target"),
    num("realise", "Realise", "Actual"),
    txt("trimestre", "Trimestre", "Quarter"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDepServiceMeeting: ConfigRegistre = {
  permModule: "departments",
  permSousModule: "service_meeting",
  tcode: "registre-service-meetings",
  icon: Icons.CalendarClock,
  titre: "Reunions de service",
  titreEn: "Service meetings",
  description: "Reunion de service avec ordre du jour et compte rendu.",
  descriptionEn: "Department meeting with agenda and minutes.",
  aide: "Le compte rendu valide la tenue et les decisions.",
  aideEn: "The minutes validate the meeting and its decisions.",
  lister: (params) => api.lister("dep-service-meetings", params),
  creer: (data) => api.creer("dep-service-meetings", data),
  modifier: (id, data) => api.modifier("dep-service-meetings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("objet", "Objet", "Subject"),
    col("date", "Date", "Date"),
    col("participants", "Participants", "Attendees"),
    col("compte_rendu", "Compte rendu", "Minutes"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("objet", "Objet", "Subject"),
    dtx("date", "Date", "Date"),
    num("participants", "Participants", "Attendees"),
    txt("compte_rendu", "Compte rendu", "Minutes"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDepProject: ConfigRegistre = {
  permModule: "departments",
  permSousModule: "project",
  tcode: "registre-projects",
  icon: Icons.FolderKanban,
  titre: "Projets internes du service",
  titreEn: "Department projects",
  description: "Projet interne porte par le departement.",
  descriptionEn: "Internal project owned by the department.",
  aide: "Le budget et l' echeance cadrent la realisation.",
  aideEn: "Budget and deadline frame the delivery.",
  lister: (params) => api.lister("dep-projects", params),
  creer: (data) => api.creer("dep-projects", data),
  modifier: (id, data) => api.modifier("dep-projects", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom", "Nom", "Name"),
    col("responsable", "Responsable", "Owner"),
    col("budget", "Budget", "Budget"),
    col("echeance", "Echeance", "Deadline"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("responsable", "Responsable", "Owner"),
    num("budget", "Budget", "Budget"),
    dt("echeance", "Echeance", "Deadline"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDepServiceRequest: ConfigRegistre = {
  permModule: "departments",
  permSousModule: "service_request",
  tcode: "registre-inter-service-requests",
  icon: Icons.ArrowLeftRight,
  titre: "Demandes inter-services",
  titreEn: "Inter-service requests",
  description: "Demande formelle d' un service vers un autre service.",
  descriptionEn: "Formal request from one department to another.",
  aide: "L' urgence et le service destinataire pilotent le traitement.",
  aideEn: "Urgency and target department drive the handling.",
  lister: (params) => api.lister("dep-service-requests", params),
  creer: (data) => api.creer("dep-service-requests", data),
  modifier: (id, data) => api.modifier("dep-service-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("objet", "Objet", "Subject"),
    col("service_destinataire", "Service destinataire", "Target department"),
    col("urgence", "Urgence", "Urgency"),
    col("date_demande", "Demande le", "Requested on"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("objet", "Objet", "Subject"),
    txt("service_destinataire", "Service destinataire", "Target department"),
    txt("urgence", "Urgence", "Urgency"),
    dt("date_demande", "Demande le", "Requested on"),
    txt("statut", "Statut", "Status"),
  ],
};

