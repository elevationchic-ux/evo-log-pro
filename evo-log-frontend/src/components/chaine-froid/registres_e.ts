/**
 * Configs Registre pour chaine-froid (expansion generee).
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

export const registreCold2TemperatureLog: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "temperature_log",
  tcode: "registre-temperature-logs",
  icon: Icons.Thermometer,
  titre: "Releves de temperature",
  titreEn: "Temperature logs",
  description: "Releve de temperature d' une unite frigorifique.",
  descriptionEn: "Temperature reading of a refrigeration unit.",
  aide: "La temperature doit rester dans la plage cible.",
  aideEn: "Temperature must stay in the target band.",
  lister: (params) => api.lister("cold2-temperature-logs", params),
  creer: (data) => api.creer("cold2-temperature-logs", data),
  modifier: (id, data) => api.modifier("cold2-temperature-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("unite", "Unite", "Unit"),
    col("temperature", "Temperature", "Temperature"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("unite", "Unite", "Unit"),
    num("temperature", "Temperature", "Temperature"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2ColdExcursion: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "cold_excursion_event",
  tcode: "registre-cold-excursion-events",
  icon: Icons.AlertTriangle,
  titre: "Excursions de temperature",
  titreEn: "Cold excursion events",
  description: "Sortie hors plage de temperature d' une cargaison.",
  descriptionEn: "Out-of-band temperature of a consignment.",
  aide: "La duree hors plage determine la perte de produit.",
  aideEn: "The out-of-band duration determines product loss.",
  lister: (params) => api.lister("cold2-cold-excursion-events", params),
  creer: (data) => api.creer("cold2-cold-excursion-events", data),
  modifier: (id, data) => api.modifier("cold2-cold-excursion-events", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("cargaison", "Cargaison", "Consignment"),
    col("temperature_max", "Temperature max", "Max temperature"),
    col("duree_min", "Duree (min)", "Duration (min)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("cargaison", "Cargaison", "Consignment"),
    num("temperature_max", "Temperature max", "Max temperature"),
    num("duree_min", "Duree (min)", "Duration (min)"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2ProbeCalibration: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "probe_calibration",
  tcode: "registre-probe-calibrations",
  icon: Icons.Gauge,
  titre: "Etalonnages de sonde",
  titreEn: "Probe calibrations",
  description: "Etalonnage d' une sonde de temperature.",
  descriptionEn: "Calibration of a temperature probe.",
  aide: "L' ecart a l' etalon valide ou non la mesure.",
  aideEn: "The deviation from the reference validates the reading.",
  lister: (params) => api.lister("cold2-probe-calibrations", params),
  creer: (data) => api.creer("cold2-probe-calibrations", data),
  modifier: (id, data) => api.modifier("cold2-probe-calibrations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("sonde", "Sonde", "Probe"),
    col("ecart", "Ecart", "Deviation"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("sonde", "Sonde", "Probe"),
    num("ecart", "Ecart", "Deviation"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2BlastFreezeCycle: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "blast_freeze_cycle",
  tcode: "registre-blast-freeze-cycles",
  icon: Icons.Snowflake,
  titre: "Cycles de surgelation",
  titreEn: "Blast freeze cycles",
  description: "Cycle de surgelation rapide d' un produit.",
  descriptionEn: "Rapid freezing cycle of a product.",
  aide: "Le temps a coeur et la temperature finale qualifient le cycle.",
  aideEn: "Core time and final temperature qualify the cycle.",
  lister: (params) => api.lister("cold2-blast-freeze-cycles", params),
  creer: (data) => api.creer("cold2-blast-freeze-cycles", data),
  modifier: (id, data) => api.modifier("cold2-blast-freeze-cycles", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("produit", "Produit", "Product"),
    col("temp_finale", "Temperature finale", "Final temperature"),
    col("duree_min", "Duree (min)", "Duration (min)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    num("temp_finale", "Temperature finale", "Final temperature"),
    num("duree_min", "Duree (min)", "Duration (min)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2DoorOpenEvent: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "door_open_event",
  tcode: "registre-door-open-events",
  icon: Icons.DoorOpen,
  titre: "Evenements d' ouverture de porte",
  titreEn: "Door open events",
  description: "Ouverture de porte d' une chambre froide.",
  descriptionEn: "Opening of a cold-room door.",
  aide: "La duree d' ouverture laisse entrer l' air chaud.",
  aideEn: "The open duration lets warm air in.",
  lister: (params) => api.lister("cold2-door-open-events", params),
  creer: (data) => api.creer("cold2-door-open-events", data),
  modifier: (id, data) => api.modifier("cold2-door-open-events", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("chambre", "Chambre", "Chamber"),
    col("duree_sec", "Duree (s)", "Duration (s)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("chambre", "Chambre", "Chamber"),
    num("duree_sec", "Duree (s)", "Duration (s)"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2HumidityLog: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "humidity_log",
  tcode: "registre-humidity-logs",
  icon: Icons.Droplet,
  titre: "Releves d' hygrometrie",
  titreEn: "Humidity logs",
  description: "Releve d' humidite relative d' une chambre.",
  descriptionEn: "Relative humidity reading of a chamber.",
  aide: "L' humidite hors plage altere le produit.",
  aideEn: "Out-of-band humidity affects the product.",
  lister: (params) => api.lister("cold2-humidity-logs", params),
  creer: (data) => api.creer("cold2-humidity-logs", data),
  modifier: (id, data) => api.modifier("cold2-humidity-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("chambre", "Chambre", "Chamber"),
    col("humidite_pct", "Humidite (%)", "Humidity (%)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("chambre", "Chambre", "Chamber"),
    num("humidite_pct", "Humidite (%)", "Humidity (%)"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2RefrigerantCharge: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "refrigerant_charge",
  tcode: "registre-refrigerant-charges",
  icon: Icons.Fan,
  titre: "Recharges de fluide frigorigene",
  titreEn: "Refrigerant charges",
  description: "Recharge / controle du fluide frigorigene d' un circuit.",
  descriptionEn: "Recharge / check of a circuit's refrigerant.",
  aide: "La quantite et le type de fluide conditionnent l' efficacité.",
  aideEn: "Quantity and fluid type condition efficiency.",
  lister: (params) => api.lister("cold2-refrigerant-charges", params),
  creer: (data) => api.creer("cold2-refrigerant-charges", data),
  modifier: (id, data) => api.modifier("cold2-refrigerant-charges", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("circuit", "Circuit", "Circuit"),
    col("fluide", "Fluide", "Fluid"),
    col("quantite_kg", "Quantite (kg)", "Quantity (kg)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("circuit", "Circuit", "Circuit"),
    txt("fluide", "Fluide", "Fluid"),
    num("quantite_kg", "Quantite (kg)", "Quantity (kg)"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2ShipmentApproval: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "cold_shipment_approval",
  tcode: "registre-cold-shipment-approvals",
  icon: Icons.CheckCircle2,
  titre: "Validations d' expedition froide",
  titreEn: "Cold shipment approvals",
  description: "Validation de pre-expedition d' une cargaison froide.",
  descriptionEn: "Pre-departure validation of a cold consignment.",
  aide: "La temperature au chargement engage la conformite du transport.",
  aideEn: "Loading temperature commits the transport conformity.",
  lister: (params) => api.lister("cold2-cold-shipment-approvals", params),
  creer: (data) => api.creer("cold2-cold-shipment-approvals", data),
  modifier: (id, data) => api.modifier("cold2-cold-shipment-approvals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("cargaison", "Cargaison", "Consignment"),
    col("temp_chargement", "Temperature chargement", "Loading temp"),
    col("valideur", "Validateur", "Approver"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("cargaison", "Cargaison", "Consignment"),
    num("temp_chargement", "Temperature chargement", "Loading temp"),
    txt("valideur", "Validateur", "Approver"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCold2IceBatteryCharge: ConfigRegistre = {
  permModule: "coldchain",
  permSousModule: "ice_battery_charge",
  tcode: "registre-ice-battery-charges",
  icon: Icons.BatteryCharging,
  titre: "Recharges de batteries de glace",
  titreEn: "Ice battery charges",
  description: "Congelation d' une batterie de glace pour caisson isotherme.",
  descriptionEn: "Freezing of an ice battery for an isothermal box.",
  aide: "Le niveau de gel conditionne l' autonomie du caisson.",
  aideEn: "Freeze level conditions the box autonomy.",
  lister: (params) => api.lister("cold2-ice-battery-charges", params),
  creer: (data) => api.creer("cold2-ice-battery-charges", data),
  modifier: (id, data) => api.modifier("cold2-ice-battery-charges", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("caisson", "Caisson", "Box"),
    col("niveau_gel", "Niveau de gel", "Freeze level"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("caisson", "Caisson", "Box"),
    txt("niveau_gel", "Niveau de gel", "Freeze level"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

