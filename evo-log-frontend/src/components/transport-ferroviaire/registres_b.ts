/**
 * Configs Registre pour transport-ferroviaire (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("transport-ferroviaire");

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

export const registreRailWheelSet: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "wheel_set",
  tcode: "registre-wheel-sets",
  icon: Icons.CircleDot,
  titre: "Essieux et roulements",
  titreEn: "Wheel sets and bearings",
  description: "Suivi des essieux par numero et kilometrage.",
  descriptionEn: "Axle tracking by number and mileage.",
  aide: "Rebut obligatoire en fin de vie.",
  aideEn: "Mandatory scrap at end of life.",
  lister: (params) => api.lister("railb-wheel-sets", params),
  creer: (data) => api.creer("railb-wheel-sets", data),
  modifier: (id, data) => api.modifier("railb-wheel-sets", id, data),
  unicite: "numero_essieu",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_essieu", "Numero essieu", "Axle number"),
    col("type_essieu", "Type essieu", "Axle type"),
    col("diametre_mm", "Diametre (mm)", "Diameter (mm)"),
    col("km_parcourus", "Km parcourus", "Km travelled"),
    col("date_controle", "Date controle", "Check date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_essieu", "Numero essieu", "Axle number", { requisCreation: true }),
    txt("type_essieu", "Type essieu", "Axle type"),
    num("diametre_mm", "Diametre (mm)", "Diameter (mm)"),
    num("km_parcourus", "Km parcourus", "Km travelled"),
    dt("date_controle", "Date controle", "Check date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailLoadingGauge: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "loading_gauge",
  tcode: "registre-loading-gauges",
  icon: Icons.Ruler,
  titre: "Gabarit de chargement",
  titreEn: "Loading gauges",
  description: "Gabarit autorise par ligne et par type de marchandise.",
  descriptionEn: "Allowed gauge per line and goods type.",
  aide: "Refuse le chargement hors gabarit.",
  aideEn: "Rejects out-of-gauge loading.",
  lister: (params) => api.lister("railb-loading-gauges", params),
  creer: (data) => api.creer("railb-loading-gauges", data),
  modifier: (id, data) => api.modifier("railb-loading-gauges", id, data),
  unicite: "code_gabarit",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_gabarit", "Code gabarit", "Gauge code"),
    col("ligne", "Ligne", "Line"),
    col("largeur_max_mm", "Largeur max (mm)", "Max width (mm)"),
    col("hauteur_max_mm", "Hauteur max (mm)", "Max height (mm)"),
    col("masse_max_t", "Masse max (t)", "Max mass (t)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_gabarit", "Code gabarit", "Gauge code", { requisCreation: true }),
    txt("ligne", "Ligne", "Line"),
    num("largeur_max_mm", "Largeur max (mm)", "Max width (mm)"),
    num("hauteur_max_mm", "Hauteur max (mm)", "Max height (mm)"),
    num("masse_max_t", "Masse max (t)", "Max mass (t)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailShuntingPlan: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "shunting_plan",
  tcode: "registre-shunting-plans",
  icon: Icons.Shuffle,
  titre: "Plans de manoeuvre",
  titreEn: "Shunting plans",
  description: "Ordre de manoeuvre des wagons en triage.",
  descriptionEn: "Wagon shunting sequence in the yard.",
  aide: "Securite : jamais de roulage libre.",
  aideEn: "Safety: no free rolling.",
  lister: (params) => api.lister("railb-shunting-plans", params),
  creer: (data) => api.creer("railb-shunting-plans", data),
  modifier: (id, data) => api.modifier("railb-shunting-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference plan", "Plan reference"),
    col("yard", "Triage", "Yard"),
    col("voie_source", "Voie source", "Source track"),
    col("voie_destinataire", "Voie destinataire", "Destination track"),
    col("nb_wagons", "Nb wagons", "Wagons"),
    col("operateur", "Operateur", "Operator"),
    col("date_plan", "Date plan", "Plan date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference plan", "Plan reference", { requisCreation: true }),
    txt("yard", "Triage", "Yard"),
    txt("voie_source", "Voie source", "Source track"),
    txt("voie_destinataire", "Voie destinataire", "Destination track"),
    num("nb_wagons", "Nb wagons", "Wagons"),
    txt("operateur", "Operateur", "Operator"),
    dtx("date_plan", "Date plan", "Plan date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailTrainConsist: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "train_consist",
  tcode: "registre-train-consists",
  icon: Icons.TrainFront,
  titre: "Composition de train",
  titreEn: "Train consists",
  description: "Liste ordonnee des wagons d une circulation.",
  descriptionEn: "Ordered list of wagons in a service.",
  aide: "Controle masse freinage et longueur.",
  aideEn: "Brake mass and length check.",
  lister: (params) => api.lister("railb-train-consists", params),
  creer: (data) => api.creer("railb-train-consists", data),
  modifier: (id, data) => api.modifier("railb-train-consists", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference composition", "Consist reference"),
    col("numero_train", "Numero train", "Train number"),
    col("nb_wagons", "Nb wagons", "Wagons"),
    col("masse_total_t", "Masse totale (t)", "Total mass (t)"),
    col("longueur_m", "Longueur (m)", "Length (m)"),
    col("locomotive", "Locomotive", "Locomotive"),
    col("date_composition", "Date composition", "Consist date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference composition", "Consist reference", { requisCreation: true }),
    txt("numero_train", "Numero train", "Train number"),
    num("nb_wagons", "Nb wagons", "Wagons"),
    num("masse_total_t", "Masse totale (t)", "Total mass (t)"),
    num("longueur_m", "Longueur (m)", "Length (m)"),
    txt("locomotive", "Locomotive", "Locomotive"),
    dtx("date_composition", "Date composition", "Consist date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailPathOccupancy: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "path_occupancy",
  tcode: "registre-path-occupancy",
  icon: Icons.CalendarRange,
  titre: "Occupation de sillons",
  titreEn: "Path occupancy",
  description: "Reservation et occupation des sillons par circulation.",
  descriptionEn: "Slot reservation and occupancy per service.",
  aide: "Conflit de sillon = refus de partance.",
  aideEn: "Slot conflict = no departure.",
  lister: (params) => api.lister("railb-path-occupancy", params),
  creer: (data) => api.creer("railb-path-occupancy", data),
  modifier: (id, data) => api.modifier("railb-path-occupancy", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference sillon", "Path reference"),
    col("numero_train", "Numero train", "Train number"),
    col("section", "Section", "Section"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("attribue_par", "Attribue par", "Granted by"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference sillon", "Path reference", { requisCreation: true }),
    txt("numero_train", "Numero train", "Train number"),
    txt("section", "Section", "Section"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    txt("attribue_par", "Attribue par", "Granted by"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailWagonDispatch: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "wagon_dispatch",
  tcode: "registre-wagon-dispatch",
  icon: Icons.ArrowDownUp,
  titre: "Affectation wagons",
  titreEn: "Wagon dispatch",
  description: "Affectation d un wagon a un client et une destination.",
  descriptionEn: "Assignment of a wagon to a client and destination.",
  aide: "Restitue le wagon vide au parc.",
  aideEn: "Returns empty wagon to pool.",
  lister: (params) => api.lister("railb-wagon-dispatch", params),
  creer: (data) => api.creer("railb-wagon-dispatch", data),
  modifier: (id, data) => api.modifier("railb-wagon-dispatch", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference affectation", "Dispatch reference"),
    col("numero_wagon", "Numero wagon", "Wagon number"),
    col("client", "Client", "Client"),
    col("destination", "Destination", "Destination"),
    col("produit", "Produit", "Product"),
    col("date_affectation", "Date affectation", "Dispatch date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference affectation", "Dispatch reference", { requisCreation: true }),
    txt("numero_wagon", "Numero wagon", "Wagon number"),
    txt("client", "Client", "Client"),
    txt("destination", "Destination", "Destination"),
    txt("produit", "Produit", "Product"),
    dt("date_affectation", "Date affectation", "Dispatch date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailTerminalCrane: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "terminal_crane",
  tcode: "registre-terminal-cranes",
  icon: Icons.Construction,
  titre: "Portiques terminaux fer",
  titreEn: "Terminal gantry cranes",
  description: "Parc portiques / reach stackers des terminaux ferrees.",
  descriptionEn: "Gantry and reach stacker fleet of rail terminals.",
  aide: "Maintenance preventive conditionne la capacite.",
  aideEn: "Preventive maintenance gates capacity.",
  lister: (params) => api.lister("railb-terminal-cranes", params),
  creer: (data) => api.creer("railb-terminal-cranes", data),
  modifier: (id, data) => api.modifier("railb-terminal-cranes", id, data),
  unicite: "code_equipment",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_equipment", "Code equipment", "Equipment code"),
    col("terminal", "Terminal", "Terminal"),
    col("type", "Type", "Type"),
    col("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    col("portee_m", "Portee (m)", "Reach (m)"),
    col("date_prochaine_visite", "Prochaine visite", "Next inspection"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_equipment", "Code equipment", "Equipment code", { requisCreation: true }),
    txt("terminal", "Terminal", "Terminal"),
    txt("type", "Type", "Type"),
    num("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    num("portee_m", "Portee (m)", "Reach (m)"),
    dt("date_prochaine_visite", "Prochaine visite", "Next inspection"),
    txt("statut", "Statut", "Status"),
  ],
};

