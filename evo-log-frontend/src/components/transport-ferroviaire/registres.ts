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

export const registreRailWagon: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "wagon_fleet",
  tcode: "registre-wagon-fleet",
  icon: Icons.TrainFront,
  titre: "Parc wagons",
  titreEn: "Rail wagon fleet",
  description: "Referentiel des wagons du parc fret (couvert, tombereau, citerne, plateau, porte-conteneurs).",
  descriptionEn: "Fleet register of freight wagons (box, gondola, tank, flat, container).",
  aide: "Revision periodique par type selon reglementation UIC.",
  aideEn: "Periodic overhaul per UIC rules.",
  lister: (params) => api.lister("rail-wagons", params),
  creer: (data) => api.creer("rail-wagons", data),
  modifier: (id, data) => api.modifier("rail-wagons", id, data),
  unicite: "numeration_wagon",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numeration_wagon", "Numeration UIC", "UIC number"),
    col("type_wagon", "Type", "Type"),
    col("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    col("livree", "Livree proprietaire", "Owner livery"),
    col("date_mise_circulation", "Mise en circulation", "In-service date"),
    col("prochaine_revision", "Prochaine revision", "Next overhaul"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numeration_wagon", "Numeration UIC", "UIC number", { requisCreation: true }),
    txt("type_wagon", "Type", "Type"),
    num("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    txt("livree", "Livree proprietaire", "Owner livery"),
    dt("date_mise_circulation", "Mise en circulation", "In-service date"),
    dt("prochaine_revision", "Prochaine revision", "Next overhaul"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailLocomotive: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "locomotive_fleet",
  tcode: "registre-locomotive-fleet",
  icon: Icons.TrainTrack,
  titre: "Parc locomotives",
  titreEn: "Locomotive fleet",
  description: "Locomotives electriques, diesels et rames automotrices.",
  descriptionEn: "Electric, diesel and EMU fleet.",
  aide: "Kilometrage decisive pour plan de maintenance.",
  aideEn: "Mileage drives maintenance plan.",
  lister: (params) => api.lister("rail-locomotives", params),
  creer: (data) => api.creer("rail-locomotives", data),
  modifier: (id, data) => api.modifier("rail-locomotives", id, data),
  unicite: "numero_series",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_series", "Numero de serie", "Series number"),
    col("modele", "Modele", "Model"),
    col("type_energie", "Energie", "Energy"),
    col("puissance_kw", "Puissance (kW)", "Power (kW)"),
    col("vitesse_max_kmh", "Vitesse max (km/h)", "Max speed"),
    col("kilometrage_actuel", "Kilometrage", "Mileage"),
    col("prochaine_revision_km", "Revision prochaine (km)", "Next overhaul (km)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_series", "Numero de serie", "Series number", { requisCreation: true }),
    txt("modele", "Modele", "Model"),
    txt("type_energie", "Energie", "Energy"),
    num("puissance_kw", "Puissance (kW)", "Power (kW)"),
    num("vitesse_max_kmh", "Vitesse max (km/h)", "Max speed"),
    num("kilometrage_actuel", "Kilometrage", "Mileage"),
    num("prochaine_revision_km", "Revision prochaine (km)", "Next overhaul (km)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailTrainPath: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "train_paths",
  tcode: "registre-train-paths",
  icon: Icons.CalendarClock,
  titre: "Sillons de circulation",
  titreEn: "Train paths",
  description: "Graphique des sillons attribues par le gestionnaire d'infrastructure.",
  descriptionEn: "Path allocation by infrastructure manager.",
  aide: "Sillon non consomme = penalite GI.",
  aideEn: "Unused path = IM penalty.",
  lister: (params) => api.lister("rail-train-paths", params),
  creer: (data) => api.creer("rail-train-paths", data),
  modifier: (id, data) => api.modifier("rail-train-paths", id, data),
  unicite: "code_sillon",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_sillon", "Code sillon", "Path code"),
    col("gare_origine", "Gare origine", "Origin station"),
    col("gare_destination", "Gare destination", "Destination station"),
    col("date_circulation", "Date", "Date"),
    col("heure_depart", "Heure depart", "Departure time"),
    col("heure_arrivee", "Heure arrivee", "Arrival time"),
    col("numero_train", "Numero train", "Train number"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_sillon", "Code sillon", "Path code", { requisCreation: true }),
    txt("gare_origine", "Gare origine", "Origin station"),
    txt("gare_destination", "Gare destination", "Destination station"),
    dt("date_circulation", "Date", "Date"),
    txt("heure_depart", "Heure depart", "Departure time"),
    txt("heure_arrivee", "Heure arrivee", "Arrival time"),
    txt("numero_train", "Numero train", "Train number"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailShuntingYard: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "shunting_yards",
  tcode: "registre-shunting-yards",
  icon: Icons.Layers,
  titre: "Gares de triage",
  titreEn: "Shunting yards",
  description: "Installations de tri et de formation des rames.",
  descriptionEn: "Classification and marshalling installations.",
  aide: "Suivi occupation voies de tri.",
  aideEn: "Track occupation tracking.",
  lister: (params) => api.lister("rail-shunting-yards", params),
  creer: (data) => api.creer("rail-shunting-yards", data),
  modifier: (id, data) => api.modifier("rail-shunting-yards", id, data),
  unicite: "code_triage",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_triage", "Code", "Code"),
    col("nom", "Nom", "Name"),
    col("localisation", "Localisation", "Location"),
    col("nb_voies_tri", "Nb voies de tri", "Classification tracks"),
    col("nb_voies_parc", "Nb voies parc", "Storage tracks"),
    col("capacite_journee_wagons", "Capacite wagons/jour", "Wagons per day"),
    col("taux_occupation_pct", "Taux occupation (%)", "Occupancy (%)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_triage", "Code", "Code", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("localisation", "Localisation", "Location"),
    num("nb_voies_tri", "Nb voies de tri", "Classification tracks"),
    num("nb_voies_parc", "Nb voies parc", "Storage tracks"),
    num("capacite_journee_wagons", "Capacite wagons/jour", "Wagons per day"),
    num("taux_occupation_pct", "Taux occupation (%)", "Occupancy (%)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailTerminal: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "rail_terminals",
  tcode: "registre-rail-terminals",
  icon: Icons.Container,
  titre: "Terminaux fer portuaires",
  titreEn: "Port rail terminals",
  description: "Interfaces terminal portuaire / reseau fer (relic modal).",
  descriptionEn: "Port-rail interface for modal shift.",
  aide: "Tracabilite du transfert container train / navire.",
  aideEn: "Container train/vessel traceability.",
  lister: (params) => api.lister("rail-terminals", params),
  creer: (data) => api.creer("rail-terminals", data),
  modifier: (id, data) => api.modifier("rail-terminals", id, data),
  unicite: "code_terminal",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_terminal", "Code terminal", "Terminal code"),
    col("port_associe", "Port associe", "Associated port"),
    col("nb_voies_fond", "Nb voies a quai", "Quay tracks"),
    col("longueur_quai_m", "Longueur quai (m)", "Quay length (m)"),
    col("equipement_manutention", "Equipement manutention", "Lifting equipment"),
    col("debit_conteneur_h", "Debit (TEU/h)", "Throughput (TEU/h)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_terminal", "Code terminal", "Terminal code", { requisCreation: true }),
    txt("port_associe", "Port associe", "Associated port"),
    num("nb_voies_fond", "Nb voies a quai", "Quay tracks"),
    num("longueur_quai_m", "Longueur quai (m)", "Quay length (m)"),
    txt("equipement_manutention", "Equipement manutention", "Lifting equipment"),
    num("debit_conteneur_h", "Debit (TEU/h)", "Throughput (TEU/h)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailConsistencyPlan: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "consistency",
  tcode: "registre-consistency-plans",
  icon: Icons.ListOrdered,
  titre: "Plans de composition",
  titreEn: "Train composition plans",
  description: "Description de la composition theorique d'un train (ordre, masse, longueur).",
  descriptionEn: "Theoretical composition per train (order, mass, length).",
  aide: "Limite longueur quai et effort traction.",
  aideEn: "Constrained by quay length and traction effort.",
  lister: (params) => api.lister("rail-consistency-plans", params),
  creer: (data) => api.creer("rail-consistency-plans", data),
  modifier: (id, data) => api.modifier("rail-consistency-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("code_sillon", "Code sillon", "Path code"),
    col("type_train", "Type train", "Train type"),
    col("nb_wagons", "Nombre wagons", "Wagons count"),
    col("masse_totale_tonnes", "Masse totale (t)", "Total mass (t)"),
    col("longueur_totale_m", "Longueur (m)", "Length (m)"),
    col("locomotive_atteltee", "Locomotive", "Locomotive"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("code_sillon", "Code sillon", "Path code"),
    txt("type_train", "Type train", "Train type"),
    num("nb_wagons", "Nombre wagons", "Wagons count"),
    num("masse_totale_tonnes", "Masse totale (t)", "Total mass (t)"),
    num("longueur_totale_m", "Longueur (m)", "Length (m)"),
    txt("locomotive_atteltee", "Locomotive", "Locomotive"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailWaybill: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "waybills",
  tcode: "registre-waybills-rail",
  icon: Icons.FileText,
  titre: "Lettres de voiture CIM/OTIF",
  titreEn: "CIM/OTIF waybills",
  description: "Titres de transport fer internationaux (CIM) ou nationaux.",
  descriptionEn: "CIM or domestic rail consignment notes.",
  aide: "Cublie obligatoire pour tout chargement.",
  aideEn: "Mandatory for every wagon loading.",
  lister: (params) => api.lister("rail-waybills", params),
  creer: (data) => api.creer("rail-waybills", data),
  modifier: (id, data) => api.modifier("rail-waybills", id, data),
  unicite: "numero_lcv",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_lcv", "Numero LCV", "Waybill number"),
    col("expediteur", "Expediteur", "Sender"),
    col("destinataire", "Destinataire", "Consignee"),
    col("gare_depart", "Gare depart", "Origin station"),
    col("gare_arrivee", "Gare arrivee", "Destination station"),
    col("date_emission", "Date emission", "Issue date"),
    col("valeur_marchandise_xaf", "Valeur marchandise", "Goods value"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_lcv", "Numero LCV", "Waybill number", { requisCreation: true }),
    txt("expediteur", "Expediteur", "Sender"),
    txt("destinataire", "Destinataire", "Consignee"),
    txt("gare_depart", "Gare depart", "Origin station"),
    txt("gare_arrivee", "Gare arrivee", "Destination station"),
    dt("date_emission", "Date emission", "Issue date"),
    num("valeur_marchandise_xaf", "Valeur marchandise", "Goods value"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailTariff: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "tariffs",
  tcode: "registre-rail-tariffs",
  icon: Icons.Calculator,
  titre: "Tarification fret fer",
  titreEn: "Rail freight tariffs",
  description: "Grille tarifaire par relation, type marchandise et tonnage.",
  descriptionEn: "Tariff grid by relation, commodity and tonnage.",
  aide: "Source UIC/OTIF + remises contractuelles.",
  aideEn: "UIC/OTIF source with contract discounts.",
  lister: (params) => api.lister("rail-tariffs", params),
  creer: (data) => api.creer("rail-tariffs", data),
  modifier: (id, data) => api.modifier("rail-tariffs", id, data),
  unicite: "code_tarif",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tarif", "Code tarif", "Tariff code"),
    col("relation", "Relation", "Route"),
    col("type_marchandise", "Type marchandise", "Commodity"),
    col("prix_par_tonne_km_xaf", "Prix (XAF/t.km)", "Price (XAF/t.km)"),
    col("remise_volume_pct", "Remise volume (%)", "Volume discount (%)"),
    col("date_debut_validite", "Debut validite", "Valid from"),
    col("date_fin_validite", "Fin validite", "Valid until"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_tarif", "Code tarif", "Tariff code", { requisCreation: true }),
    txt("relation", "Relation", "Route"),
    txt("type_marchandise", "Type marchandise", "Commodity"),
    num("prix_par_tonne_km_xaf", "Prix (XAF/t.km)", "Price (XAF/t.km)"),
    num("remise_volume_pct", "Remise volume (%)", "Volume discount (%)"),
    dt("date_debut_validite", "Debut validite", "Valid from"),
    dt("date_fin_validite", "Fin validite", "Valid until"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailWagonTracking: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "tracking",
  tcode: "registre-wagon-tracking",
  icon: Icons.MapPin,
  titre: "Suivi wagons / telegrammes RID",
  titreEn: "Wagon tracking / RID telegrams",
  description: "Position et etat de chaque wagon en temps reel via CID/TELEGRAMMES.",
  descriptionEn: "Real-time wagon position via CID/RID telegrams.",
  aide: "Retrecage wagons critiques (matieres dangereuses).",
  aideEn: "Narrowing for dangerous goods.",
  lister: (params) => api.lister("rail-wagon-tracking", params),
  creer: (data) => api.creer("rail-wagon-tracking", data),
  modifier: (id, data) => api.modifier("rail-wagon-tracking", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("numeration_wagon", "Numeration wagon", "Wagon number"),
    col("code_lcv", "Code LCV", "Waybill code"),
    col("gare_actuelle", "Gare actuelle", "Current station"),
    col("date_position", "Horodatage position", "Position timestamp"),
    col("evenement", "Evenement", "Event"),
    col("geolocalisation_gps", "GPS", "GPS"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("numeration_wagon", "Numeration wagon", "Wagon number"),
    txt("code_lcv", "Code LCV", "Waybill code"),
    txt("gare_actuelle", "Gare actuelle", "Current station"),
    dtx("date_position", "Horodatage position", "Position timestamp"),
    txt("evenement", "Evenement", "Event"),
    txt("geolocalisation_gps", "GPS", "GPS"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailWagonMaintenance: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "maintenance",
  tcode: "registre-wagon-maintenance",
  icon: Icons.Wrench,
  titre: "Maintenance parc wagon",
  titreEn: "Wagon maintenance",
  description: "Ateliers, revisions periodiques et immobilisations techniques.",
  descriptionEn: "Workshops, periodic overhauls and technical holds.",
  aide: "Revision decennale obligatoire (UIC 541).",
  aideEn: "Mandatory decennial overhaul (UIC 541).",
  lister: (params) => api.lister("rail-wagon-maintenance", params),
  creer: (data) => api.creer("rail-wagon-maintenance", data),
  modifier: (id, data) => api.modifier("rail-wagon-maintenance", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference ordre", "Work order reference"),
    col("numeration_wagon", "Wagon concerne", "Wagon number"),
    col("atelier", "Atelier", "Workshop"),
    col("type_intervention", "Type intervention", "Intervention type"),
    col("date_debut", "Date debut", "Start date"),
    col("date_fin_prevue", "Fin prevue", "Planned end"),
    col("date_retour_service", "Retour service", "Return to service"),
    col("cout_xaf", "Cout", "Cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference ordre", "Work order reference", { requisCreation: true }),
    txt("numeration_wagon", "Wagon concerne", "Wagon number"),
    txt("atelier", "Atelier", "Workshop"),
    txt("type_intervention", "Type intervention", "Intervention type"),
    dt("date_debut", "Date debut", "Start date"),
    dt("date_fin_prevue", "Fin prevue", "Planned end"),
    dt("date_retour_service", "Retour service", "Return to service"),
    num("cout_xaf", "Cout", "Cost"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailSafetyRecord: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "safety",
  tcode: "registre-rail-safety",
  icon: Icons.ShieldAlert,
  titre: "Securite circulations",
  titreEn: "Circulation safety",
  description: "ETCS / signalisation / incidents securite ferroviaire.",
  descriptionEn: "ETCS, signalling and safety incidents.",
  aide: "Rapport obligatoire EPSF dans les 24h pour incident grave.",
  aideEn: "Mandatory EPSF report within 24h for serious incidents.",
  lister: (params) => api.lister("rail-safety-records", params),
  creer: (data) => api.creer("rail-safety-records", data),
  modifier: (id, data) => api.modifier("rail-safety-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference rapport", "Report reference"),
    col("date_evenement", "Date evenement", "Event date"),
    col("type_incident", "Type incident", "Incident type"),
    col("gravite", "Gravite", "Severity"),
    col("lgn_concernee", "Ligne concernee", "Line involved"),
    col("wagon_train_implique", "Wagon/train implique", "Wagon/train involved"),
    col("description", "Description", "Description"),
    col("mesure_correctrice", "Mesure corrective", "Corrective measure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference rapport", "Report reference", { requisCreation: true }),
    dtx("date_evenement", "Date evenement", "Event date"),
    txt("type_incident", "Type incident", "Incident type"),
    txt("gravite", "Gravite", "Severity"),
    txt("lgn_concernee", "Ligne concernee", "Line involved"),
    txt("wagon_train_implique", "Wagon/train implique", "Wagon/train involved"),
    txt("description", "Description", "Description"),
    txt("mesure_correctrice", "Mesure corrective", "Corrective measure"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRailCorridor: ConfigRegistre = {
  permModule: "ferroviaire",
  permSousModule: "corridors",
  tcode: "registre-intermodal-corridors",
  icon: Icons.Route,
  titre: "Corridors fer-port",
  titreEn: "Rail-port corridors",
  description: "Cartographie des corridors logistiques (Dorsal, Abidjan-Lagos, Douane Yaounde-Douala).",
  descriptionEn: "Map of logistics corridors (Dorsal, Abidjan-Lagos, Yaounde-Douala customs).",
  aide: "Coordination multi-operateurs / RFF.",
  aideEn: "Multi-operator / rail-infrastructure coordination.",
  lister: (params) => api.lister("rail-corridors", params),
  creer: (data) => api.creer("rail-corridors", data),
  modifier: (id, data) => api.modifier("rail-corridors", id, data),
  unicite: "code_corridor",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_corridor", "Code corridor", "Corridor code"),
    col("nom", "Nom", "Name"),
    col("pays_traverses", "Pays traverses", "Countries"),
    col("longueur_km", "Longueur (km)", "Length (km)"),
    col("gares_focales", "Gares focales", "Hub stations"),
    col("operateurs", "Operateurs", "Operators"),
    col("debit_annuel_teu", "Debit annuel TEU", "Annual TEU"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_corridor", "Code corridor", "Corridor code", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("pays_traverses", "Pays traverses", "Countries"),
    num("longueur_km", "Longueur (km)", "Length (km)"),
    txt("gares_focales", "Gares focales", "Hub stations"),
    txt("operateurs", "Operateurs", "Operators"),
    num("debit_annuel_teu", "Debit annuel TEU", "Annual TEU"),
    txt("statut", "Statut", "Status"),
  ],
};

