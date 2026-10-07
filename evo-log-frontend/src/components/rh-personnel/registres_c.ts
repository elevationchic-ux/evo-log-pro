/**
 * Configs Registre pour rh-personnel (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("rh-personnel");

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

export const registreRhCTrainingPlan: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "training_plan",
  tcode: "registre-training-plans",
  icon: Icons.GraduationCap,
  titre: "Plans de formation",
  titreEn: "Training plans",
  description: "Plan individuel ou collectif de developpement des competences.",
  descriptionEn: "Individual or collective skills development plan.",
  aide: "Heures financees vs heures realisees suivies par plan.",
  aideEn: "Funded vs delivered hours tracked per plan.",
  lister: (params) => api.lister("rhc-training-plans", params),
  creer: (data) => api.creer("rhc-training-plans", data),
  modifier: (id, data) => api.modifier("rhc-training-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference plan", "Plan reference"),
    col("intitule", "Intitule", "Title"),
    col("categorie", "Categorie", "Category"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("organisme", "Organisme", "Provider"),
    col("heures_financees", "Heures financees", "Funded hours"),
    col("heures_realisees", "Heures realisees", "Delivered hours"),
    col("date_debut", "Date debut", "Start date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference plan", "Plan reference", { requisCreation: true }),
    txt("intitule", "Intitule", "Title"),
    txt("categorie", "Categorie", "Category"),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("organisme", "Organisme", "Provider"),
    num("heures_financees", "Heures financees", "Funded hours"),
    num("heures_realisees", "Heures realisees", "Delivered hours"),
    dt("date_debut", "Date debut", "Start date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRhCDisciplinaryRecord: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "disciplinary_record",
  tcode: "registre-disciplinary-records",
  icon: Icons.Gavel,
  titre: "Registre disciplinaire",
  titreEn: "Disciplinary records",
  description: "Consigne des sanctions et mesures disciplinaires.",
  descriptionEn: "Log of sanctions and disciplinary measures.",
  aide: "Chaque sanction reference un motif et une date d'effet.",
  aideEn: "Each sanction references a reason and an effective date.",
  lister: (params) => api.lister("rhc-disciplinary-records", params),
  creer: (data) => api.creer("rhc-disciplinary-records", data),
  modifier: (id, data) => api.modifier("rhc-disciplinary-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference dossier", "Case reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("type_sanction", "Type de sanction", "Sanction type"),
    col("motif", "Motif", "Reason"),
    col("date_effet", "Date d'effet", "Effective date"),
    col("date_fin_effet", "Fin d'effet", "End date"),
    col("decideur", "Decideur", "Decision maker"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference dossier", "Case reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("type_sanction", "Type de sanction", "Sanction type"),
    txt("motif", "Motif", "Reason"),
    dt("date_effet", "Date d'effet", "Effective date"),
    dt("date_fin_effet", "Fin d'effet", "End date"),
    txt("decideur", "Decideur", "Decision maker"),
    txt("statut", "Statut", "Status"),
  ],
};

