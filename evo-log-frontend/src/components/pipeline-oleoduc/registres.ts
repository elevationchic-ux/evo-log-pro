/**
 * Configs Registre pour pipeline-oleoduc (expansion wave 5 generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("pipeline-oleoduc");

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


export const registreSection: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "sections",
  tcode: "registre-sections",
  icon: Icons.Pipeline,
  titre: "Troncons de pipeline",
  titreEn: "Pipeline sections",
  description: "Sections physiques du reseau (troncon, diametre, produit transporté).",
  descriptionEn: "Physical sections of the network.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("sections", params),
  creer: (data) => api.creer("sections", data),
  modifier: (id, data) => api.modifier("sections", id, data),
  unicite: "code_section",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_section", "Code Section", "Section code"),
    col("nom", "Nom", "Nom"),
    col("type_produit", "Type Produit", "Type Produit"),
    col("diametre_mm", "Diametre Mm", "Diametre Mm"),
    col("epaisseur_paroi_mm", "Epaisseur Paroi Mm", "Epaisseur Paroi Mm"),
    col("longueur_km", "Longueur Km", "Longueur Km"),
    col("origine", "Origine", "Origine"),
    col("destination", "Destination", "Destination"),
    col("date_mise_service", "Date Mise Service", "Date Mise Service"),
    col("pression_max_bar", "Pression Max Bar", "Pression Max Bar"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_section", "Code Section", "Section code", { requisCreation: true }),
    txt("nom", "Nom", "Nom"),
    txt("type_produit", "Type Produit", "Type Produit"),
    num("diametre_mm", "Diametre Mm", "Diametre Mm"),
    num("epaisseur_paroi_mm", "Epaisseur Paroi Mm", "Epaisseur Paroi Mm"),
    num("longueur_km", "Longueur Km", "Longueur Km"),
    txt("origine", "Origine", "Origine"),
    txt("destination", "Destination", "Destination"),
    dt("date_mise_service", "Date Mise Service", "Date Mise Service"),
    num("pression_max_bar", "Pression Max Bar", "Pression Max Bar"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePumpStation: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "pump_stations",
  tcode: "registre-pump-stations",
  icon: Icons.Zap,
  titre: "Stations de pompage",
  titreEn: "Pump stations",
  description: "Stations de compression/pompage et postes de sectionnement.",
  descriptionEn: "Compression/pumping stations.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("pump-stations", params),
  creer: (data) => api.creer("pump-stations", data),
  modifier: (id, data) => api.modifier("pump-stations", id, data),
  unicite: "code_station",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_station", "Code Station", "Station code"),
    col("nom", "Nom", "Nom"),
    col("type_station", "Type Station", "Type Station"),
    col("section_associee", "Section Associee", "Section Associee"),
    col("nb_pompes", "Nb Pompes", "Nb Pompes"),
    col("puissance_totale_kw", "Puissance Totale Kw", "Puissance Totale Kw"),
    col("debit_nominal_m3h", "Debit Nominal M3h", "Debit Nominal M3h"),
    col("pression_refoulement_bar", "Pression Refoulement Bar", "Pression Refoulement Bar"),
    col("energie_annuelle_kwh", "Energie Annuelle Kwh", "Energie Annuelle Kwh"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_station", "Code Station", "Station code", { requisCreation: true }),
    txt("nom", "Nom", "Nom"),
    txt("type_station", "Type Station", "Type Station"),
    txt("section_associee", "Section Associee", "Section Associee"),
    num("nb_pompes", "Nb Pompes", "Nb Pompes"),
    num("puissance_totale_kw", "Puissance Totale Kw", "Puissance Totale Kw"),
    num("debit_nominal_m3h", "Debit Nominal M3h", "Debit Nominal M3h"),
    num("pression_refoulement_bar", "Pression Refoulement Bar", "Pression Refoulement Bar"),
    num("energie_annuelle_kwh", "Energie Annuelle Kwh", "Energie Annuelle Kwh"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreStorageTank: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "storage_tanks",
  tcode: "registre-storage-tanks",
  icon: Icons.Database,
  titre: "Cuves de stockage",
  titreEn: "Storage tanks",
  description: "Bacs de stockage hydrocarbures (fixes et flottants).",
  descriptionEn: "Hydrocarbon storage tanks.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("storage-tanks", params),
  creer: (data) => api.creer("storage-tanks", data),
  modifier: (id, data) => api.modifier("storage-tanks", id, data),
  unicite: "code_cuve",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_cuve", "Code Cuve", "Tank code"),
    col("type_cuve", "Type Cuve", "Type Cuve"),
    col("capacite_m3", "Capacite M3", "Capacite M3"),
    col("niveau_actuel_pct", "Niveau Actuel Pct", "Niveau Actuel Pct"),
    col("temperature_stockage_c", "Temperature Stockage C", "Temperature Stockage C"),
    col("produit_stocke", "Produit Stocke", "Produit Stocke"),
    col("date_dernier_nettoyage", "Date Dernier Nettoyage", "Date Dernier Nettoyage"),
    col("prochaine_inspection", "Prochaine Inspection", "Prochaine Inspection"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_cuve", "Code Cuve", "Tank code", { requisCreation: true }),
    txt("type_cuve", "Type Cuve", "Type Cuve"),
    num("capacite_m3", "Capacite M3", "Capacite M3"),
    num("niveau_actuel_pct", "Niveau Actuel Pct", "Niveau Actuel Pct"),
    num("temperature_stockage_c", "Temperature Stockage C", "Temperature Stockage C"),
    txt("produit_stocke", "Produit Stocke", "Produit Stocke"),
    dt("date_dernier_nettoyage", "Date Dernier Nettoyage", "Date Dernier Nettoyage"),
    dt("prochaine_inspection", "Prochaine Inspection", "Prochaine Inspection"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMeteringPoint: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "metering_points",
  tcode: "registre-metering-points",
  icon: Icons.Gauge,
  titre: "Points de mesure",
  titreEn: "Metering points",
  description: "Systemes de comptage fiscal et commercial (turbinex, coriolis).",
  descriptionEn: "Fiscal/commercial metering skids.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("metering-points", params),
  creer: (data) => api.creer("metering-points", data),
  modifier: (id, data) => api.modifier("metering-points", id, data),
  unicite: "code_point",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_point", "Code Point", "Point code"),
    col("usage", "Usage", "Usage"),
    col("technologie", "Technologie", "Technologie"),
    col("section_associee", "Section Associee", "Section Associee"),
    col("precision_pct", "Precision Pct", "Precision Pct"),
    col("debit_max_m3h", "Debit Max M3h", "Debit Max M3h"),
    col("date_etalonnage", "Date Etalonnage", "Date Etalonnage"),
    col("prochain_etalonnage", "Prochain Etalonnage", "Prochain Etalonnage"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_point", "Code Point", "Point code", { requisCreation: true }),
    txt("usage", "Usage", "Usage"),
    txt("technologie", "Technologie", "Technologie"),
    txt("section_associee", "Section Associee", "Section Associee"),
    num("precision_pct", "Precision Pct", "Precision Pct"),
    num("debit_max_m3h", "Debit Max M3h", "Debit Max M3h"),
    dt("date_etalonnage", "Date Etalonnage", "Date Etalonnage"),
    dt("prochain_etalonnage", "Prochain Etalonnage", "Prochain Etalonnage"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProductBatch: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "product_batches",
  tcode: "registre-product-batches",
  icon: Icons.Layers,
  titre: "Lot produit",
  titreEn: "Product batch",
  description: "Batch de produit (essence, gasoil, jet, brut) injecte.",
  descriptionEn: "Batch of injected product.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("product-batches", params),
  creer: (data) => api.creer("product-batches", data),
  modifier: (id, data) => api.modifier("product-batches", id, data),
  unicite: "numero_lot",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_lot", "Numero Lot", "Batch number"),
    col("produit", "Produit", "Produit"),
    col("volume_m3", "Volume (m3)", "Volume M3"),
    col("densite_api", "Densite Api", "Densite Api"),
    col("teneur_soufre_pct", "Teneur Soufre Pct", "Teneur Soufre Pct"),
    col("injection_debut", "Injection Debut", "Injection Debut"),
    col("arrivee_prevue", "Arrivee Prevue", "Arrivee Prevue"),
    col("destinataire", "Destinataire", "Destinataire"),
    col("section_utilisee", "Section Utilisee", "Section Utilisee"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_lot", "Numero Lot", "Batch number", { requisCreation: true }),
    txt("produit", "Produit", "Produit"),
    num("volume_m3", "Volume (m3)", "Volume M3"),
    num("densite_api", "Densite Api", "Densite Api"),
    num("teneur_soufre_pct", "Teneur Soufre Pct", "Teneur Soufre Pct"),
    dtx("injection_debut", "Injection Debut", "Injection Debut"),
    dtx("arrivee_prevue", "Arrivee Prevue", "Arrivee Prevue"),
    txt("destinataire", "Destinataire", "Destinataire"),
    txt("section_utilisee", "Section Utilisee", "Section Utilisee"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePressureReading: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "pressure_readings",
  tcode: "registre-pressure-readings",
  icon: Icons.Activity,
  titre: "Releves de pression",
  titreEn: "Pressure readings",
  description: "Telemétrie pression / debit par section.",
  descriptionEn: "Pressure/flow telemetry per section.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("pressure-readings", params),
  creer: (data) => api.creer("pressure-readings", data),
  modifier: (id, data) => api.modifier("pressure-readings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("section_associee", "Section Associee", "Section Associee"),
    col("date_releve", "Date Releve", "Date Releve"),
    col("pression_entree_bar", "Pression Entree Bar", "Pression Entree Bar"),
    col("pression_sortie_bar", "Pression Sortie Bar", "Pression Sortie Bar"),
    col("debit_m3h", "Debit M3h", "Debit M3h"),
    col("temperature_c", "Temperature C", "Temperature C"),
    col("qualite", "Qualite", "Qualite"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("section_associee", "Section Associee", "Section Associee"),
    dtx("date_releve", "Date Releve", "Date Releve"),
    num("pression_entree_bar", "Pression Entree Bar", "Pression Entree Bar"),
    num("pression_sortie_bar", "Pression Sortie Bar", "Pression Sortie Bar"),
    num("debit_m3h", "Debit M3h", "Debit M3h"),
    num("temperature_c", "Temperature C", "Temperature C"),
    txt("qualite", "Qualite", "Qualite"),
  ],
};


export const registreLeakDetection: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "leak_detections",
  tcode: "registre-leak-detections",
  icon: Icons.Radar,
  titre: "Detection fuites",
  titreEn: "Leak detection",
  description: "Campaignes HG-PVT / aeralia / fibre optique.",
  descriptionEn: "Negative pressure / fibre leak detection.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("leak-detections", params),
  creer: (data) => api.creer("leak-detections", data),
  modifier: (id, data) => api.modifier("leak-detections", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("date_detection", "Date Detection", "Date Detection"),
    col("section_associee", "Section Associee", "Section Associee"),
    col("technologie", "Technologie", "Technologie"),
    col("perte_estimee_m3", "Perte Estimee M3", "Perte Estimee M3"),
    col("severite", "Severite", "Severite"),
    col("lat_localisation", "Lat Localisation", "Lat Localisation"),
    col("lon_localisation", "Lon Localisation", "Lon Localisation"),
    col("delai_reparation_h", "Delai Reparation H", "Delai Reparation H"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    dtx("date_detection", "Date Detection", "Date Detection"),
    txt("section_associee", "Section Associee", "Section Associee"),
    txt("technologie", "Technologie", "Technologie"),
    num("perte_estimee_m3", "Perte Estimee M3", "Perte Estimee M3"),
    txt("severite", "Severite", "Severite"),
    txt("lat_localisation", "Lat Localisation", "Lat Localisation"),
    txt("lon_localisation", "Lon Localisation", "Lon Localisation"),
    num("delai_reparation_h", "Delai Reparation H", "Delai Reparation H"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMaintWork: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "maintenance_works",
  tcode: "registre-maintenance-works",
  icon: Icons.Wrench,
  titre: "Travaux maintenance",
  titreEn: "Maintenance works",
  description: "Pigging, soudures, protections cathodiques.",
  descriptionEn: "Pigging / welding / CP works.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("maintenance-works", params),
  creer: (data) => api.creer("maintenance-works", data),
  modifier: (id, data) => api.modifier("maintenance-works", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("section_associee", "Section Associee", "Section Associee"),
    col("type_travaux", "Type Travaux", "Type Travaux"),
    col("date_debut", "Date debut", "Date Debut"),
    col("date_fin_prevue", "Fin prevue", "Date Fin Prevue"),
    col("date_fin_reelle", "Date Fin Reelle", "Date Fin Reelle"),
    col("cout_xaf", "Cout (XAF)", "Cout Xaf"),
    col("prestataire", "Prestataire", "Prestataire"),
    col("arret_production_h", "Arret Production H", "Arret Production H"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("section_associee", "Section Associee", "Section Associee"),
    txt("type_travaux", "Type Travaux", "Type Travaux"),
    dt("date_debut", "Date debut", "Date Debut"),
    dt("date_fin_prevue", "Fin prevue", "Date Fin Prevue"),
    dt("date_fin_reelle", "Date Fin Reelle", "Date Fin Reelle"),
    num("cout_xaf", "Cout (XAF)", "Cout Xaf"),
    txt("prestataire", "Prestataire", "Prestataire"),
    num("arret_production_h", "Arret Production H", "Arret Production H"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreInjectCampaign: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "injection_campaigns",
  tcode: "registre-injection-campaigns",
  icon: Icons.Upload,
  titre: "Campagnes d'injection",
  titreEn: "Injection campaigns",
  description: "Campagnes d'admission produit dans le reseau.",
  descriptionEn: "Product admission campaigns.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("injection-campaigns", params),
  creer: (data) => api.creer("injection-campaigns", data),
  modifier: (id, data) => api.modifier("injection-campaigns", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("type", "Type", "Type"),
    col("section_associee", "Section Associee", "Section Associee"),
    col("produit_chimique", "Produit Chimique", "Produit Chimique"),
    col("debit_injection_lh", "Debit Injection Lh", "Debit Injection Lh"),
    col("date_debut", "Date debut", "Date Debut"),
    col("date_fin", "Date fin", "Date Fin"),
    col("volume_total_l", "Volume Total L", "Volume Total L"),
    col("cout_xaf", "Cout (XAF)", "Cout Xaf"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("type", "Type", "Type"),
    txt("section_associee", "Section Associee", "Section Associee"),
    txt("produit_chimique", "Produit Chimique", "Produit Chimique"),
    num("debit_injection_lh", "Debit Injection Lh", "Debit Injection Lh"),
    dt("date_debut", "Date debut", "Date Debut"),
    dt("date_fin", "Date fin", "Date Fin"),
    num("volume_total_l", "Volume Total L", "Volume Total L"),
    num("cout_xaf", "Cout (XAF)", "Cout Xaf"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreShipNomination: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "ship_nominations",
  tcode: "registre-ship-nominations",
  icon: Icons.Ship,
  titre: "Nominations navires (ship-or)",
  titreEn: "Ship nominations",
  description: "Nominations de navires pour chargement (ship-or).",
  descriptionEn: "Vessel nominations (ship-or).",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("ship-nominations", params),
  creer: (data) => api.creer("ship-nominations", data),
  modifier: (id, data) => api.modifier("ship-nominations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom_navire", "Nom Navire", "Nom Navire"),
    col("imo", "Imo", "Imo"),
    col("terminal", "Terminal", "Terminal"),
    col("produit_charge", "Produit Charge", "Produit Charge"),
    col("volume_m3", "Volume (m3)", "Volume M3"),
    col("eta", "Eta", "Eta"),
    col("etb", "Etb", "Etb"),
    col("etc", "Etc", "Etc"),
    col("vacis", "Vacis", "Vacis"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom_navire", "Nom Navire", "Nom Navire"),
    txt("imo", "Imo", "Imo"),
    txt("terminal", "Terminal", "Terminal"),
    txt("produit_charge", "Produit Charge", "Produit Charge"),
    num("volume_m3", "Volume (m3)", "Volume M3"),
    dt("eta", "Eta", "Eta"),
    dt("etb", "Etb", "Etb"),
    dt("etc", "Etc", "Etc"),
    txt("vacis", "Vacis", "Vacis"),
    txt("statut", "Statut", "Status"),
  ],
};

