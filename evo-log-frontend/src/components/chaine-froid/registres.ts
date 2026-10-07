/**
 * Configs Registre pour chaine-froid (expansion wave 5 generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("chaine-froid");

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


export const registreChambre: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "chambers",
  tcode: "registre-chambers",
  icon: Icons.Snowflake,
  titre: "Chambres froides",
  titreEn: "Cold rooms",
  description: "Entrepots refroidis (positif/negatif).",
  descriptionEn: "Positive/negative cold storage.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("chambers", params),
  creer: (data) => api.creer("chambers", data),
  modifier: (id, data) => api.modifier("chambers", id, data),
  unicite: "code_chambre",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_chambre", "Code Chambre", "Room code"),
    col("type_chambre", "Type Chambre", "Type Chambre"),
    col("plage", "Plage", "Plage"),
    col("temperature_consigne_c", "Temperature Consigne C", "Temperature Consigne C"),
    col("temperature_actuelle_c", "Temperature Actuelle C", "Temperature Actuelle C"),
    col("capacite_m3", "Capacite M3", "Capacite M3"),
    col("puissance_kw", "Puissance Kw", "Puissance Kw"),
    col("date_mise_service", "Date Mise Service", "Date Mise Service"),
    col("prochaine_maintenance", "Prochaine Maintenance", "Prochaine Maintenance"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_chambre", "Code Chambre", "Room code", { requisCreation: true }),
    txt("type_chambre", "Type Chambre", "Type Chambre"),
    txt("plage", "Plage", "Plage"),
    num("temperature_consigne_c", "Temperature Consigne C", "Temperature Consigne C"),
    num("temperature_actuelle_c", "Temperature Actuelle C", "Temperature Actuelle C"),
    num("capacite_m3", "Capacite M3", "Capacite M3"),
    num("puissance_kw", "Puissance Kw", "Puissance Kw"),
    dt("date_mise_service", "Date Mise Service", "Date Mise Service"),
    dt("prochaine_maintenance", "Prochaine Maintenance", "Prochaine Maintenance"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreReefer: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "reefers",
  tcode: "registre-reefers",
  icon: Icons.Container,
  titre: "Conteneurs frigorifiques (reefer)",
  titreEn: "Reefer containers",
  description: "Reefer 20/40/45' et gensets.",
  descriptionEn: "20/40/45' reefer + genset.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("reefers", params),
  creer: (data) => api.creer("reefers", data),
  modifier: (id, data) => api.modifier("reefers", id, data),
  unicite: "numero_reefer",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_reefer", "Numero Reefer", "Reefer number"),
    col("type_reefer", "Type Reefer", "Type Reefer"),
    col("mode", "Mode", "Mode"),
    col("plage_temperature_c", "Plage Temperature C", "Plage Temperature C"),
    col("capacite_m3", "Capacite M3", "Capacite M3"),
    col("date_last_check", "Date Last Check", "Date Last Check"),
    col("prochaine_pt", "Prochaine Pt", "Prochaine Pt"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_reefer", "Numero Reefer", "Reefer number", { requisCreation: true }),
    txt("type_reefer", "Type Reefer", "Type Reefer"),
    txt("mode", "Mode", "Mode"),
    txt("plage_temperature_c", "Plage Temperature C", "Plage Temperature C"),
    num("capacite_m3", "Capacite M3", "Capacite M3"),
    dt("date_last_check", "Date Last Check", "Date Last Check"),
    dt("prochaine_pt", "Prochaine Pt", "Prochaine Pt"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreLogger: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "loggers",
  tcode: "registre-loggers",
  icon: Icons.Thermometer,
  titre: "Enregistreurs temperature",
  titreEn: "Temperature loggers",
  description: "Data logger RFID / NFC / Bluetooth.",
  descriptionEn: "RFID / NFC / Bluetooth loggers.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("loggers", params),
  creer: (data) => api.creer("loggers", data),
  modifier: (id, data) => api.modifier("loggers", id, data),
  unicite: "numero_logger",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_logger", "Numero Logger", "Logger number"),
    col("technologie", "Technologie", "Technologie"),
    col("frequence_lecture_s", "Frequence Lecture S", "Frequence Lecture S"),
    col("autonomie_jours", "Autonomie Jours", "Autonomie Jours"),
    col("precision_c", "Precision C", "Precision C"),
    col("date_achat", "Date Achat", "Date Achat"),
    col("date_calibration", "Date Calibration", "Date Calibration"),
    col("prochaine_calibration", "Prochaine Calibration", "Prochaine Calibration"),
    col("assigned_to", "Assigned To", "Assigned To"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_logger", "Numero Logger", "Logger number", { requisCreation: true }),
    txt("technologie", "Technologie", "Technologie"),
    num("frequence_lecture_s", "Frequence Lecture S", "Frequence Lecture S"),
    num("autonomie_jours", "Autonomie Jours", "Autonomie Jours"),
    num("precision_c", "Precision C", "Precision C"),
    dt("date_achat", "Date Achat", "Date Achat"),
    dt("date_calibration", "Date Calibration", "Date Calibration"),
    dt("prochaine_calibration", "Prochaine Calibration", "Prochaine Calibration"),
    txt("assigned_to", "Assigned To", "Assigned To"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreSku: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "products",
  tcode: "registre-products",
  icon: Icons.Boxes,
  titre: "Produits refrigeres (SKU)",
  titreEn: "Cold products (SKU)",
  description: "Marchandises avec plage temperature.",
  descriptionEn: "Goods with temperature range.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("products", params),
  creer: (data) => api.creer("products", data),
  modifier: (id, data) => api.modifier("products", id, data),
  unicite: "code_sku",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_sku", "Code Sku", "SKU code"),
    col("nom", "Nom", "Nom"),
    col("categorie", "Categorie", "Categorie"),
    col("classe", "Classe", "Classe"),
    col("temp_min_c", "Temp Min C", "Temp Min C"),
    col("temp_max_c", "Temp Max C", "Temp Max C"),
    col("duree_vie_jours", "Duree Vie Jours", "Duree Vie Jours"),
    col("seuil_excursion_h", "Seuil Excursion H", "Seuil Excursion H"),
  ],
  champs: [
    txt("code_sku", "Code Sku", "SKU code", { requisCreation: true }),
    txt("nom", "Nom", "Nom"),
    txt("categorie", "Categorie", "Categorie"),
    txt("classe", "Classe", "Classe"),
    num("temp_min_c", "Temp Min C", "Temp Min C"),
    num("temp_max_c", "Temp Max C", "Temp Max C"),
    num("duree_vie_jours", "Duree Vie Jours", "Duree Vie Jours"),
    num("seuil_excursion_h", "Seuil Excursion H", "Seuil Excursion H"),
  ],
};


export const registreExcursion: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "excursions",
  tcode: "registre-excursions",
  icon: Icons.AlertTriangle,
  titre: "Excursions temperature",
  titreEn: "Temperature excursions",
  description: "Ecart hors tolerance documente.",
  descriptionEn: "Out-of-tolerance event.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("excursions", params),
  creer: (data) => api.creer("excursions", data),
  modifier: (id, data) => api.modifier("excursions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("type", "Type", "Type"),
    col("produit_concerne", "Produit Concerne", "Produit Concerne"),
    col("actif_associe", "Actif Associe", "Actif Associe"),
    col("date_debut", "Date debut", "Date Debut"),
    col("date_fin", "Date fin", "Date Fin"),
    col("temp_extreme_c", "Temp Extreme C", "Temp Extreme C"),
    col("duree_h", "Duree H", "Duree H"),
    col("impact", "Impact", "Impact"),
    col("valeur_perdue_xaf", "Valeur Perdue Xaf", "Valeur Perdue Xaf"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("type", "Type", "Type"),
    txt("produit_concerne", "Produit Concerne", "Produit Concerne"),
    txt("actif_associe", "Actif Associe", "Actif Associe"),
    dtx("date_debut", "Date debut", "Date Debut"),
    dtx("date_fin", "Date fin", "Date Fin"),
    num("temp_extreme_c", "Temp Extreme C", "Temp Extreme C"),
    num("duree_h", "Duree H", "Duree H"),
    txt("impact", "Impact", "Impact"),
    num("valeur_perdue_xaf", "Valeur Perdue Xaf", "Valeur Perdue Xaf"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreVaccinBatch: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "vaccin_batches",
  tcode: "registre-vaccin-batches",
  icon: Icons.Syringe,
  titre: "Lots de vaccins",
  titreEn: "Vaccine batches",
  description: "Suivi VPM + phase d'utilisation.",
  descriptionEn: "EPI vaccine batch tracking.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("vaccin-batches", params),
  creer: (data) => api.creer("vaccin-batches", data),
  modifier: (id, data) => api.modifier("vaccin-batches", id, data),
  unicite: "numero_lot",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_lot", "Numero Lot", "Batch number"),
    col("fabricant", "Fabricant", "Fabricant"),
    col("type_vaccin", "Type Vaccin", "Type Vaccin"),
    col("nb_doses", "Nb Doses", "Nb Doses"),
    col("date_fabrication", "Date Fabrication", "Date Fabrication"),
    col("date_peremption", "Date Peremption", "Date Peremption"),
    col("temp_stockage_c", "Temp Stockage C", "Temp Stockage C"),
    col("vvm_statut", "Vvm Statut", "Vvm Statut"),
    col("lieu_stockage", "Lieu Stockage", "Lieu Stockage"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_lot", "Numero Lot", "Batch number", { requisCreation: true }),
    txt("fabricant", "Fabricant", "Fabricant"),
    txt("type_vaccin", "Type Vaccin", "Type Vaccin"),
    num("nb_doses", "Nb Doses", "Nb Doses"),
    dt("date_fabrication", "Date Fabrication", "Date Fabrication"),
    dt("date_peremption", "Date Peremption", "Date Peremption"),
    num("temp_stockage_c", "Temp Stockage C", "Temp Stockage C"),
    txt("vvm_statut", "Vvm Statut", "Vvm Statut"),
    txt("lieu_stockage", "Lieu Stockage", "Lieu Stockage"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHaccp: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "haccp_records",
  tcode: "registre-haccp-records",
  icon: Icons.Shield,
  titre: "Enregistrements HACCP",
  titreEn: "HACCP records",
  description: "Points critiques et surveillance.",
  descriptionEn: "Critical control point monitoring.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("haccp-records", params),
  creer: (data) => api.creer("haccp-records", data),
  modifier: (id, data) => api.modifier("haccp-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("pratique", "Pratique", "Pratique"),
    col("date_lecture", "Date Lecture", "Date Lecture"),
    col("valeur_lue", "Valeur Lue", "Valeur Lue"),
    col("seuil_mini", "Seuil Mini", "Seuil Mini"),
    col("seuil_maxi", "Seuil Maxi", "Seuil Maxi"),
    col("operateur", "Operateur", "Operateur"),
    col("action_corrective", "Action Corrective", "Action Corrective"),
    col("resultat", "Resultat", "Resultat"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("pratique", "Pratique", "Pratique"),
    dtx("date_lecture", "Date Lecture", "Date Lecture"),
    txt("valeur_lue", "Valeur Lue", "Valeur Lue"),
    txt("seuil_mini", "Seuil Mini", "Seuil Mini"),
    txt("seuil_maxi", "Seuil Maxi", "Seuil Maxi"),
    txt("operateur", "Operateur", "Operateur"),
    area("action_corrective", "Action Corrective", "Action Corrective"),
    txt("resultat", "Resultat", "Resultat"),
  ],
};


export const registreDefrost: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "defrost_cycles",
  tcode: "registre-defrost-cycles",
  icon: Icons.RefreshCcw,
  titre: "Cycles de dégivrage",
  titreEn: "Defrost cycles",
  description: "Givrage / désinfection périodique.",
  descriptionEn: "Icing / periodic sanitation.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("defrost-cycles", params),
  creer: (data) => api.creer("defrost-cycles", data),
  modifier: (id, data) => api.modifier("defrost-cycles", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("chambre_associee", "Chambre Associee", "Chambre Associee"),
    col("frequence", "Frequence", "Frequence"),
    col("type", "Type", "Type"),
    col("date_prevue", "Date Prevue", "Date Prevue"),
    col("date_reelle_debut", "Date Reelle Debut", "Date Reelle Debut"),
    col("date_reelle_fin", "Date Reelle Fin", "Date Reelle Fin"),
    col("duree_h", "Duree H", "Duree H"),
    col("energie_kwh", "Energie Kwh", "Energie Kwh"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("chambre_associee", "Chambre Associee", "Chambre Associee"),
    txt("frequence", "Frequence", "Frequence"),
    txt("type", "Type", "Type"),
    dt("date_prevue", "Date Prevue", "Date Prevue"),
    dtx("date_reelle_debut", "Date Reelle Debut", "Date Reelle Debut"),
    dtx("date_reelle_fin", "Date Reelle Fin", "Date Reelle Fin"),
    num("duree_h", "Duree H", "Duree H"),
    num("energie_kwh", "Energie Kwh", "Energie Kwh"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEnergyMeter: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "energy_meters",
  tcode: "registre-energy-meters",
  icon: Icons.Zap,
  titre: "Compteurs energie",
  titreEn: "Energy meters",
  description: "Conso kWh chambres + reefers.",
  descriptionEn: "Cold room + reefer kWh usage.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("energy-meters", params),
  creer: (data) => api.creer("energy-meters", data),
  modifier: (id, data) => api.modifier("energy-meters", id, data),
  unicite: "code_compteur",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_compteur", "Code Compteur", "Meter code"),
    col("type_energie", "Type Energie", "Type Energie"),
    col("actif_alimente", "Actif Alimente", "Actif Alimente"),
    col("consommation_kwh", "Consommation Kwh", "Consommation Kwh"),
    col("cout_mensuel_xaf", "Cout Mensuel Xaf", "Cout Mensuel Xaf"),
    col("co2_eq_kg", "Co2 Eq Kg", "Co2 Eq Kg"),
    col("date_releve", "Date Releve", "Date Releve"),
  ],
  champs: [
    txt("code_compteur", "Code Compteur", "Meter code", { requisCreation: true }),
    txt("type_energie", "Type Energie", "Type Energie"),
    txt("actif_alimente", "Actif Alimente", "Actif Alimente"),
    num("consommation_kwh", "Consommation Kwh", "Consommation Kwh"),
    num("cout_mensuel_xaf", "Cout Mensuel Xaf", "Cout Mensuel Xaf"),
    num("co2_eq_kg", "Co2 Eq Kg", "Co2 Eq Kg"),
    dt("date_releve", "Date Releve", "Date Releve"),
  ],
};


export const registreTransportLeg: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "transport_legs",
  tcode: "registre-transport-legs",
  icon: Icons.Truck,
  titre: "Segment de transport frigorifique",
  titreEn: "Cold transport leg",
  description: "Leg routier/fer/air avec temperature suivie.",
  descriptionEn: "Truck/rail/air leg with T°.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("transport-legs", params),
  creer: (data) => api.creer("transport-legs", data),
  modifier: (id, data) => api.modifier("transport-legs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("mode", "Mode", "Mode"),
    col("reefer_utilise", "Reefer Utilise", "Reefer Utilise"),
    col("produit_transporte", "Produit Transporte", "Produit Transporte"),
    col("poids_kg", "Poids (kg)", "Poids Kg"),
    col("origine", "Origine", "Origine"),
    col("destination", "Destination", "Destination"),
    col("date_depart", "Date Depart", "Date Depart"),
    col("date_arrivee", "Date Arrivee", "Date Arrivee"),
    col("temp_moyenne_c", "Temp Moyenne C", "Temp Moyenne C"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("mode", "Mode", "Mode"),
    txt("reefer_utilise", "Reefer Utilise", "Reefer Utilise"),
    txt("produit_transporte", "Produit Transporte", "Produit Transporte"),
    num("poids_kg", "Poids (kg)", "Poids Kg"),
    txt("origine", "Origine", "Origine"),
    txt("destination", "Destination", "Destination"),
    dtx("date_depart", "Date Depart", "Date Depart"),
    dtx("date_arrivee", "Date Arrivee", "Date Arrivee"),
    num("temp_moyenne_c", "Temp Moyenne C", "Temp Moyenne C"),
    txt("statut", "Statut", "Status"),
  ],
};

