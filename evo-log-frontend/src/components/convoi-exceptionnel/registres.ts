/**
 * Configs Registre pour convoi-exceptionnel (expansion wave 5 generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("convoi-exceptionnel");

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


export const registreHLProject: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "projects",
  tcode: "registre-projects",
  icon: Icons.HardHat,
  titre: "Projets project-cargo",
  titreEn: "Project cargo",
  description: "Colis exceptionnels, tours, reacteurs, eoliennes.",
  descriptionEn: "Turbines, towers, reactors.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("projects", params),
  creer: (data) => api.creer("projects", data),
  modifier: (id, data) => api.modifier("projects", id, data),
  unicite: "code_projet",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_projet", "Code Projet", "Project code"),
    col("nom", "Nom", "Nom"),
    col("client", "Client", "Client"),
    col("categorie", "Categorie", "Categorie"),
    col("poids_max_t", "Poids max (t)", "Poids Max T"),
    col("volume_m3", "Volume (m3)", "Volume M3"),
    col("distance_km", "Distance (km)", "Distance Km"),
    col("date_debut", "Date debut", "Date Debut"),
    col("date_fin_prevue", "Fin prevue", "Date Fin Prevue"),
    col("budget_xaf", "Budget (XAF)", "Budget Xaf"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_projet", "Code Projet", "Project code", { requisCreation: true }),
    txt("nom", "Nom", "Nom"),
    txt("client", "Client", "Client"),
    txt("categorie", "Categorie", "Categorie"),
    num("poids_max_t", "Poids max (t)", "Poids Max T"),
    num("volume_m3", "Volume (m3)", "Volume M3"),
    num("distance_km", "Distance (km)", "Distance Km"),
    dt("date_debut", "Date debut", "Date Debut"),
    dt("date_fin_prevue", "Fin prevue", "Date Fin Prevue"),
    num("budget_xaf", "Budget (XAF)", "Budget Xaf"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLCrane: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "cranes",
  tcode: "registre-cranes",
  icon: Icons.Construction,
  titre: "Grues & engins de levage",
  titreEn: "Cranes & lifting gear",
  description: "Mobility / crawler / tower.",
  descriptionEn: "Mobile / crawler / tower.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("cranes", params),
  creer: (data) => api.creer("cranes", data),
  modifier: (id, data) => api.modifier("cranes", id, data),
  unicite: "numero_grue",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_grue", "Numero Grue", "Crane number"),
    col("type_grue", "Type Grue", "Type Grue"),
    col("capacite_max_t", "Capacite max (t)", "Capacite Max T"),
    col("portee_max_m", "Portee Max M", "Portee Max M"),
    col("hauteur_max_m", "Hauteur Max M", "Hauteur Max M"),
    col("mise_en_service", "Mise En Service", "Mise En Service"),
    col("prochaine_visite", "Prochaine Visite", "Prochaine Visite"),
    col("cout_location_jour_xaf", "Cout Location Jour Xaf", "Cout Location Jour Xaf"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_grue", "Numero Grue", "Crane number", { requisCreation: true }),
    txt("type_grue", "Type Grue", "Type Grue"),
    num("capacite_max_t", "Capacite max (t)", "Capacite Max T"),
    num("portee_max_m", "Portee Max M", "Portee Max M"),
    num("hauteur_max_m", "Hauteur Max M", "Hauteur Max M"),
    dt("mise_en_service", "Mise En Service", "Mise En Service"),
    dt("prochaine_visite", "Prochaine Visite", "Prochaine Visite"),
    num("cout_location_jour_xaf", "Cout Location Jour Xaf", "Cout Location Jour Xaf"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLTrailer: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "modular_trailers",
  tcode: "registre-modular-trailers",
  icon: Icons.Truck,
  titre: "Remorques modulaires",
  titreEn: "Modular trailers",
  description: "Plateaux SPMT / multi-essieux.",
  descriptionEn: "SPMT / multi-axle flats.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("modular-trailers", params),
  creer: (data) => api.creer("modular-trailers", data),
  modifier: (id, data) => api.modifier("modular-trailers", id, data),
  unicite: "plaque",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("plaque", "Plaque", "Plate"),
    col("type_remorque", "Type Remorque", "Type Remorque"),
    col("nb_essieux", "Nb Essieux", "Nb Essieux"),
    col("charge_utile_t", "Charge Utile T", "Charge Utile T"),
    col("longueur_m", "Longueur M", "Longueur M"),
    col("largeur_m", "Largeur M", "Largeur M"),
    col("hauteur_min_m", "Hauteur Min M", "Hauteur Min M"),
    col("angle_orientation_deg", "Angle Orientation Deg", "Angle Orientation Deg"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("plaque", "Plaque", "Plate", { requisCreation: true }),
    txt("type_remorque", "Type Remorque", "Type Remorque"),
    num("nb_essieux", "Nb Essieux", "Nb Essieux"),
    num("charge_utile_t", "Charge Utile T", "Charge Utile T"),
    num("longueur_m", "Longueur M", "Longueur M"),
    num("largeur_m", "Largeur M", "Largeur M"),
    num("hauteur_min_m", "Hauteur Min M", "Hauteur Min M"),
    num("angle_orientation_deg", "Angle Orientation Deg", "Angle Orientation Deg"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLSurvey: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "route_surveys",
  tcode: "registre-route-surveys",
  icon: Icons.Map,
  titre: "Etudes d'itineraire",
  titreEn: "Route surveys",
  description: "Reconnaissance ponts/cables/obstacles.",
  descriptionEn: "Bridge/cable/obstacle survey.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("route-surveys", params),
  creer: (data) => api.creer("route-surveys", data),
  modifier: (id, data) => api.modifier("route-surveys", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("projet_associe", "Projet Associe", "Projet Associe"),
    col("origine", "Origine", "Origine"),
    col("destination", "Destination", "Destination"),
    col("distance_km", "Distance (km)", "Distance Km"),
    col("nb_obstacles", "Nb Obstacles", "Nb Obstacles"),
    col("ouvrages_franchis", "Ouvrages Franchis", "Ouvrages Franchis"),
    col("cout_amenagement_xaf", "Cout Amenagement Xaf", "Cout Amenagement Xaf"),
    col("date_etude", "Date Etude", "Date Etude"),
    col("resultat", "Resultat", "Resultat"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("projet_associe", "Projet Associe", "Projet Associe"),
    txt("origine", "Origine", "Origine"),
    txt("destination", "Destination", "Destination"),
    num("distance_km", "Distance (km)", "Distance Km"),
    num("nb_obstacles", "Nb Obstacles", "Nb Obstacles"),
    area("ouvrages_franchis", "Ouvrages Franchis", "Ouvrages Franchis"),
    num("cout_amenagement_xaf", "Cout Amenagement Xaf", "Cout Amenagement Xaf"),
    dt("date_etude", "Date Etude", "Date Etude"),
    txt("resultat", "Resultat", "Resultat"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLLiftPlan: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "lift_plans",
  tcode: "registre-lift-plans",
  icon: Icons.ClipboardList,
  titre: "Plans de levage",
  titreEn: "Lift plans",
  description: "Decription methodique du lift.",
  descriptionEn: "Methodical lift description.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("lift-plans", params),
  creer: (data) => api.creer("lift-plans", data),
  modifier: (id, data) => api.modifier("lift-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("projet_associe", "Projet Associe", "Projet Associe"),
    col("type_operation", "Type Operation", "Type Operation"),
    col("charge_t", "Charge T", "Charge T"),
    col("hauteur_m", "Hauteur M", "Hauteur M"),
    col("centre_gravite_haut", "Centre Gravite Haut", "Centre Gravite Haut"),
    col("coefficient_securite_pct", "Coefficient Securite Pct", "Coefficient Securite Pct"),
    col("grue_prevue", "Grue Prevue", "Grue Prevue"),
    col("date_prevue", "Date Prevue", "Date Prevue"),
    col("criticite", "Criticite", "Criticite"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("projet_associe", "Projet Associe", "Projet Associe"),
    txt("type_operation", "Type Operation", "Type Operation"),
    num("charge_t", "Charge T", "Charge T"),
    num("hauteur_m", "Hauteur M", "Hauteur M"),
    chk("centre_gravite_haut", "Centre Gravite Haut", "Centre Gravite Haut"),
    num("coefficient_securite_pct", "Coefficient Securite Pct", "Coefficient Securite Pct"),
    txt("grue_prevue", "Grue Prevue", "Grue Prevue"),
    dt("date_prevue", "Date Prevue", "Date Prevue"),
    txt("criticite", "Criticite", "Criticite"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLPermit: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "permits",
  tcode: "registre-permits",
  icon: Icons.FileSignature,
  titre: "Autorisations & permis",
  titreEn: "Permits & authorizations",
  description: "Convoi hors gabarit / voirie / port.",
  descriptionEn: "Overdimension / road / port.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("permits", params),
  creer: (data) => api.creer("permits", data),
  modifier: (id, data) => api.modifier("permits", id, data),
  unicite: "numero_permis",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_permis", "Numero Permis", "Permit number"),
    col("type_permis", "Type Permis", "Type Permis"),
    col("autorite", "Autorite", "Autorite"),
    col("charge_concernee", "Charge Concernee", "Charge Concernee"),
    col("itineraire_depot", "Itineraire Depot", "Itineraire Depot"),
    col("date_depot_demande", "Date Depot Demande", "Date Depot Demande"),
    col("date_delivrance", "Date Delivrance", "Date Delivrance"),
    col("date_validite_fin", "Date Validite Fin", "Date Validite Fin"),
    col("cout_redevance_xaf", "Cout Redevance Xaf", "Cout Redevance Xaf"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_permis", "Numero Permis", "Permit number", { requisCreation: true }),
    txt("type_permis", "Type Permis", "Type Permis"),
    txt("autorite", "Autorite", "Autorite"),
    txt("charge_concernee", "Charge Concernee", "Charge Concernee"),
    area("itineraire_depot", "Itineraire Depot", "Itineraire Depot"),
    dt("date_depot_demande", "Date Depot Demande", "Date Depot Demande"),
    dt("date_delivrance", "Date Delivrance", "Date Delivrance"),
    dt("date_validite_fin", "Date Validite Fin", "Date Validite Fin"),
    num("cout_redevance_xaf", "Cout Redevance Xaf", "Cout Redevance Xaf"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLEscort: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "escorts",
  tcode: "registre-escorts",
  icon: Icons.Shield,
  titre: "Escortes & balisage",
  titreEn: "Escorts & pilotage",
  description: "Vehicules + agents + gendarmerie.",
  descriptionEn: "Vehicle + agents + police.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("escorts", params),
  creer: (data) => api.creer("escorts", data),
  modifier: (id, data) => api.modifier("escorts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("convoi_associe", "Convoi Associe", "Convoi Associe"),
    col("type_escorte", "Type Escorte", "Type Escorte"),
    col("nb_vehicules_escorte", "Nb Vehicules Escorte", "Nb Vehicules Escorte"),
    col("date_debut", "Date debut", "Date Debut"),
    col("date_fin", "Date fin", "Date Fin"),
    col("zone_administrative", "Zone Administrative", "Zone Administrative"),
    col("agent_responsable", "Agent Responsable", "Agent Responsable"),
    col("cout_xaf", "Cout (XAF)", "Cout Xaf"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("convoi_associe", "Convoi Associe", "Convoi Associe"),
    txt("type_escorte", "Type Escorte", "Type Escorte"),
    num("nb_vehicules_escorte", "Nb Vehicules Escorte", "Nb Vehicules Escorte"),
    dtx("date_debut", "Date debut", "Date Debut"),
    dtx("date_fin", "Date fin", "Date Fin"),
    txt("zone_administrative", "Zone Administrative", "Zone Administrative"),
    txt("agent_responsable", "Agent Responsable", "Agent Responsable"),
    num("cout_xaf", "Cout (XAF)", "Cout Xaf"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLLashing: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "lashings",
  tcode: "registre-lashings",
  icon: Icons.Link,
  titre: "Arrimage / lashing",
  titreEn: "Lashing",
  description: "Chaine / sangle / effort.",
  descriptionEn: "Chain / strap / tension.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("lashings", params),
  creer: (data) => api.creer("lashings", data),
  modifier: (id, data) => api.modifier("lashings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("methode", "Methode", "Methode"),
    col("charge_amarree", "Charge Amarree", "Charge Amarree"),
    col("nb_points", "Nb Points", "Nb Points"),
    col("effort_admissible_t", "Effort Admissible T", "Effort Admissible T"),
    col("coefficient_secu_pct", "Coefficient Secu Pct", "Coefficient Secu Pct"),
    col("operateur", "Operateur", "Operateur"),
    col("date_controle", "Date Controle", "Date Controle"),
    col("resultat", "Resultat", "Resultat"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("methode", "Methode", "Methode"),
    txt("charge_amarree", "Charge Amarree", "Charge Amarree"),
    num("nb_points", "Nb Points", "Nb Points"),
    num("effort_admissible_t", "Effort Admissible T", "Effort Admissible T"),
    num("coefficient_secu_pct", "Coefficient Secu Pct", "Coefficient Secu Pct"),
    txt("operateur", "Operateur", "Operateur"),
    dt("date_controle", "Date Controle", "Date Controle"),
    txt("resultat", "Resultat", "Resultat"),
  ],
};


export const registreHLBallast: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "ballasts",
  tcode: "registre-ballasts",
  icon: Icons.Weight,
  titre: "Lest / ballast",
  titreEn: "Ballast",
  description: "Masses additionnelles de stabilisation.",
  descriptionEn: "Extra stabilization mass.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("ballasts", params),
  creer: (data) => api.creer("ballasts", data),
  modifier: (id, data) => api.modifier("ballasts", id, data),
  unicite: "code_ballast",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_ballast", "Code Ballast", "Ballast code"),
    col("type_ballast", "Type Ballast", "Type Ballast"),
    col("masse_unitaire_t", "Masse Unitaire T", "Masse Unitaire T"),
    col("nb_unites", "Nb Unites", "Nb Unites"),
    col("masse_totale_t", "Masse Totale T", "Masse Totale T"),
    col("cout_location_jour_xaf", "Cout Location Jour Xaf", "Cout Location Jour Xaf"),
    col("lieu_stockage", "Lieu Stockage", "Lieu Stockage"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_ballast", "Code Ballast", "Ballast code", { requisCreation: true }),
    txt("type_ballast", "Type Ballast", "Type Ballast"),
    num("masse_unitaire_t", "Masse Unitaire T", "Masse Unitaire T"),
    num("nb_unites", "Nb Unites", "Nb Unites"),
    num("masse_totale_t", "Masse Totale T", "Masse Totale T"),
    num("cout_location_jour_xaf", "Cout Location Jour Xaf", "Cout Location Jour Xaf"),
    txt("lieu_stockage", "Lieu Stockage", "Lieu Stockage"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHLRigging: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "rigging_methods",
  tcode: "registre-rigging-methods",
  icon: Icons.Workflow,
  titre: "Methodes de rigging",
  titreEn: "Rigging methods",
  description: "Elingage, palonnage, poutre de charge.",
  descriptionEn: "Slings / spreaders / beams.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("rigging-methods", params),
  creer: (data) => api.creer("rigging-methods", data),
  modifier: (id, data) => api.modifier("rigging-methods", id, data),
  unicite: "code_methode",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_methode", "Code Methode", "Method code"),
    col("categorie", "Categorie", "Categorie"),
    col("description", "Description", "Description"),
    col("capacite_max_t", "Capacite max (t)", "Capacite Max T"),
    col("temps_mise_en_oeuvre_h", "Temps Mise En Oeuvre H", "Temps Mise En Oeuvre H"),
    col("nb_techniciens", "Nb Techniciens", "Nb Techniciens"),
    col("cout_moyen_xaf", "Cout Moyen Xaf", "Cout Moyen Xaf"),
  ],
  champs: [
    txt("code_methode", "Code Methode", "Method code", { requisCreation: true }),
    txt("categorie", "Categorie", "Categorie"),
    area("description", "Description", "Description"),
    num("capacite_max_t", "Capacite max (t)", "Capacite Max T"),
    num("temps_mise_en_oeuvre_h", "Temps Mise En Oeuvre H", "Temps Mise En Oeuvre H"),
    num("nb_techniciens", "Nb Techniciens", "Nb Techniciens"),
    num("cout_moyen_xaf", "Cout Moyen Xaf", "Cout Moyen Xaf"),
  ],
};

