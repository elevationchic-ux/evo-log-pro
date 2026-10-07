/**
 * Configs Registre pour transport-aerien (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("transport-aerien");

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

export const registreHouseAirWaybill: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "house_waybill",
  tcode: "registre-house-waybills",
  icon: Icons.FileText,
  titre: "Lettres de transport house (HAWB)",
  titreEn: "House air waybills",
  description: "Fractions consolidees sous une MAWB.",
  descriptionEn: "Consolidated fractions under a master AWB.",
  aide: "L agent de fret emet le HAWB au client.",
  aideEn: "Forwarder issues HAWB to client.",
  lister: (params) => api.lister("airb-house-waybills", params),
  creer: (data) => api.creer("airb-house-waybills", data),
  modifier: (id, data) => api.modifier("airb-house-waybills", id, data),
  unicite: "numero_hawb",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_hawb", "Numero HAWB", "HAWB number"),
    col("numero_mawb", "Numero MAWB", "MAWB number"),
    col("expediteur", "Expediteur", "Shipper"),
    col("destinataire", "Destinataire", "Consignee"),
    col("nb_colis", "Nb colis", "Pieces"),
    col("poids_kg", "Poids (kg)", "Weight (kg)"),
    col("nature_marchandise", "Nature marchandise", "Goods type"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_hawb", "Numero HAWB", "HAWB number", { requisCreation: true }),
    txt("numero_mawb", "Numero MAWB", "MAWB number"),
    txt("expediteur", "Expediteur", "Shipper"),
    txt("destinataire", "Destinataire", "Consignee"),
    num("nb_colis", "Nb colis", "Pieces"),
    num("poids_kg", "Poids (kg)", "Weight (kg)"),
    txt("nature_marchandise", "Nature marchandise", "Goods type"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePerishableCargo: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "perishable_cargo",
  tcode: "registre-perishable-cargo",
  icon: Icons.Snowflake,
  titre: "Fret perishable (chaine du froid)",
  titreEn: "Perishable cargo",
  description: "Marchandises perissables sous temperature dirigee.",
  descriptionEn: "Temperature-controlled perishable goods.",
  aide: "Respect des delais IATA PERishable.",
  aideEn: "IATA perishable time limits.",
  lister: (params) => api.lister("airb-perishable-cargo", params),
  creer: (data) => api.creer("airb-perishable-cargo", data),
  modifier: (id, data) => api.modifier("airb-perishable-cargo", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("numero_mawb", "MAWB", "MAWB"),
    col("produit", "Produit", "Product"),
    col("plage_temp_c", "Plage temperature (C)", "Temp range (C)"),
    col("poids_kg", "Poids (kg)", "Weight (kg)"),
    col("date_embarquement", "Embarquement", "Loading time"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("numero_mawb", "MAWB", "MAWB"),
    txt("produit", "Produit", "Product"),
    txt("plage_temp_c", "Plage temperature (C)", "Temp range (C)"),
    num("poids_kg", "Poids (kg)", "Weight (kg)"),
    dtx("date_embarquement", "Embarquement", "Loading time"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreLiveAnimalShipment: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "live_animal",
  tcode: "registre-live-animal-shipments",
  icon: Icons.PawPrint,
  titre: "Fret vivant (animaux)",
  titreEn: "Live animal shipments",
  description: "Transport d animaux vivants conforme CRDA.",
  descriptionEn: "Live animal transport compliant with CRDA.",
  aide: "Conteneurs et ventilation homologues.",
  aideEn: "Approved containers and ventilation.",
  lister: (params) => api.lister("airb-live-animals", params),
  creer: (data) => api.creer("airb-live-animals", data),
  modifier: (id, data) => api.modifier("airb-live-animals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("numero_mawb", "MAWB", "MAWB"),
    col("espece", "Espece", "Species"),
    col("nb_animaux", "Nb animaux", "Animals"),
    col("type_conteneur", "Type conteneur", "Container type"),
    col("date_depart", "Depart", "Departure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("numero_mawb", "MAWB", "MAWB"),
    txt("espece", "Espece", "Species"),
    num("nb_animaux", "Nb animaux", "Animals"),
    txt("type_conteneur", "Type conteneur", "Container type"),
    dtx("date_depart", "Depart", "Departure"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCharteredFlight: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "chartered_flight",
  tcode: "registre-chartered-flights",
  icon: Icons.PlaneTakeoff,
  titre: "Vols affretes",
  titreEn: "Chartered flights",
  description: "Affretements ad hoc pour fret ou projet.",
  descriptionEn: "Ad hoc charters for cargo or projects.",
  aide: "Contrat d affretement et creneau reserve.",
  aideEn: "Charter agreement and slot reserved.",
  lister: (params) => api.lister("airb-chartered-flights", params),
  creer: (data) => api.creer("airb-chartered-flights", data),
  modifier: (id, data) => api.modifier("airb-chartered-flights", id, data),
  unicite: "numero_affretement",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_affretement", "Numero affretement", "Charter number"),
    col("client", "Client", "Client"),
    col("immatriculation", "Aéronef", "Aircraft"),
    col("depart_aeroport", "Aeroport depart", "Origin airport"),
    col("arrivee_aeroport", "Aeroport arrivee", "Destination airport"),
    col("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    col("date_vol", "Date vol", "Flight date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_affretement", "Numero affretement", "Charter number", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("immatriculation", "Aéronef", "Aircraft"),
    txt("depart_aeroport", "Aeroport depart", "Origin airport"),
    txt("arrivee_aeroport", "Aeroport arrivee", "Destination airport"),
    num("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    dtx("date_vol", "Date vol", "Flight date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAirCustomsClearance: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "customs_clearance",
  tcode: "registre-customs-clearance-air",
  icon: Icons.Stamp,
  titre: "Dedouanement fret aerien",
  titreEn: "Air customs clearance",
  description: "Dossiers de dechargement et formalites douane aeroport.",
  descriptionEn: "Aircraft offload and airport customs formalities.",
  aide: "Bloque la mise a disposition tant que non decharge.",
  aideEn: "Blocks release until cleared.",
  lister: (params) => api.lister("airb-customs-clearance", params),
  creer: (data) => api.creer("airb-customs-clearance", data),
  modifier: (id, data) => api.modifier("airb-customs-clearance", id, data),
  unicite: "numero_dossier",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_dossier", "Numero dossier", "File number"),
    col("numero_mawb", "MAWB", "MAWB"),
    col("type_operation", "Type operation", "Operation type"),
    col("bureau_douane", "Bureau de douane", "Customs office"),
    col("droits_xaf", "Droits (XAF)", "Duties (XAF)"),
    col("date_depot", "Date depot", "Filing date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_dossier", "Numero dossier", "File number", { requisCreation: true }),
    txt("numero_mawb", "MAWB", "MAWB"),
    txt("type_operation", "Type operation", "Operation type"),
    txt("bureau_douane", "Bureau de douane", "Customs office"),
    num("droits_xaf", "Droits (XAF)", "Duties (XAF)"),
    dt("date_depot", "Date depot", "Filing date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreApronMovement: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "apron_movement",
  tcode: "registre-apron-movements",
  icon: Icons.Move,
  titre: "Mouvements piste (apron)",
  titreEn: "Apron movements",
  description: "Mouvements aéronefs et vehicules piste par poste.",
  descriptionEn: "Aircraft and ground vehicle movements per stand.",
  aide: "Coordination PRA / marshaller.",
  aideEn: "Stand and marshaller coordination.",
  lister: (params) => api.lister("airb-apron-movements", params),
  creer: (data) => api.creer("airb-apron-movements", data),
  modifier: (id, data) => api.modifier("airb-apron-movements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference mouvement", "Movement reference"),
    col("poste_parc", "Poste de parc", "Stand"),
    col("immatriculation", "Aéronef", "Aircraft"),
    col("type_mouvement", "Type mouvement", "Movement type"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference mouvement", "Movement reference", { requisCreation: true }),
    txt("poste_parc", "Poste de parc", "Stand"),
    txt("immatriculation", "Aéronef", "Aircraft"),
    txt("type_mouvement", "Type mouvement", "Movement type"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreNoiseComplianceRecord: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "noise_compliance",
  tcode: "registre-noise-compliance",
  icon: Icons.VolumeX,
  titre: "Conformite nuisances sonores",
  titreEn: "Noise compliance",
  description: "Mesures et conformite bruit des aéronefs / restrictions nocturnes.",
  descriptionEn: "Aircraft noise measurements and curfew compliance.",
  aide: "Sanction possible si depassement quota.",
  aideEn: "Sanction if quota exceeded.",
  lister: (params) => api.lister("airb-noise-compliance", params),
  creer: (data) => api.creer("airb-noise-compliance", data),
  modifier: (id, data) => api.modifier("airb-noise-compliance", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference mesure", "Measurement reference"),
    col("immatriculation", "Aéronef", "Aircraft"),
    col("coefficient_bruit_db", "Coefficient bruit (dB)", "Noise coefficient (dB)"),
    col("creneau", "Creneau", "Time window"),
    col("date_mesure", "Date mesure", "Measure date"),
    col("quota_consomme", "Quota consomme", "Quota used"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference mesure", "Measurement reference", { requisCreation: true }),
    txt("immatriculation", "Aéronef", "Aircraft"),
    num("coefficient_bruit_db", "Coefficient bruit (dB)", "Noise coefficient (dB)"),
    txt("creneau", "Creneau", "Time window"),
    dt("date_mesure", "Date mesure", "Measure date"),
    num("quota_consomme", "Quota consomme", "Quota used"),
    txt("statut", "Statut", "Status"),
  ],
};

