/**
 * Configs Registre pour parc-vehicules (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("parc-vehicules");

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

export const registreVehicleInventory: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "vehicle_inventory",
  tcode: "registre-vehicle-inventory",
  icon: Icons.Truck,
  titre: "Inventaire complet du parc",
  titreEn: "Full fleet inventory",
  description: "Liste detaillee des vehicules avec attributs.",
  descriptionEn: "Detailed fleet list with attributes.",
  aide: "Chaque entree correspond a un numerò de serie unique.",
  aideEn: "Each entry corresponds to a unique serial number.",
  lister: (params) => api.lister("vehicle-inventories", params),
  creer: (data) => api.creer("vehicle-inventories", data),
  modifier: (id, data) => api.modifier("vehicle-inventories", id, data),
  unicite: "numero_serie",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_serie", "Numero serie", "Serial number"),
    col("marque", "Marque", "Brand"),
    col("modele", "Modele", "Model"),
    col("annee", "Annee", "Year"),
    col("carrosserie", "Carrosserie", "Body"),
    col("energie", "Energie", "Energy"),
    col("kilometrage", "Kilometrage", "Mileage"),
    col("cout_acquisition_xaf", "Cout acquisition", "Acquisition cost"),
    col("valeur_argent_xaf", "Valeur veneur", "Market value"),
  ],
  champs: [
    txt("numero_serie", "Numero serie", "Serial number", { requisCreation: true }),
    txt("marque", "Marque", "Brand"),
    txt("modele", "Modele", "Model"),
    num("annee", "Annee", "Year"),
    txt("carrosserie", "Carrosserie", "Body"),
    sel("energie", "Energie", "Energy", "energie"),
    num("kilometrage", "Kilometrage", "Mileage"),
    num("cout_acquisition_xaf", "Cout acquisition", "Acquisition cost"),
    num("valeur_argent_xaf", "Valeur veneur", "Market value"),
  ],
};


export const registreTyreRecord: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "tyre_management",
  tcode: "registre-tyre-management",
  icon: Icons.CircleDot,
  titre: "Gestion pneumatiques",
  titreEn: "Tyre management",
  description: "Suivi des gommes par vehicule.",
  descriptionEn: "Tyre tracking per vehicle.",
  aide: "Rotation tous les 15 000 km recommande.",
  aideEn: "Rotation every 15,000 km recommended.",
  lister: (params) => api.lister("tyre-records", params),
  creer: (data) => api.creer("tyre-records", data),
  modifier: (id, data) => api.modifier("tyre-records", id, data),
  unicite: "numero_gomme",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_gomme", "Numero gomme", "Tyre number"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("dimension", "Dimension", "Size"),
    col("marque", "Marque", "Brand"),
    col("position", "Position", "Position"),
    col("km_parcourus", "Km parcourus", "Kilometers"),
    col("profondeur_couronne_mm", "Profondeur couronne (mm)", "Tread depth (mm)"),
    col("date_montage", "Date montage", "Mount date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_gomme", "Numero gomme", "Tyre number", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    txt("dimension", "Dimension", "Size"),
    txt("marque", "Marque", "Brand"),
    sel("position", "Position", "Position", "position"),
    num("km_parcourus", "Km parcourus", "Kilometers"),
    num("profondeur_couronne_mm", "Profondeur couronne (mm)", "Tread depth (mm)"),
    dt("date_montage", "Date montage", "Mount date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSparePart: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "spare_part",
  tcode: "registre-spare-parts",
  icon: Icons.Cog,
  titre: "Pieces detachees / stock atelier",
  titreEn: "Spare parts / workshop stock",
  description: "Consommables et pieces atelier.",
  descriptionEn: "Workshop consumables and parts.",
  aide: "Seuil mini et conditionnement a respecter.",
  aideEn: "Min threshold and packaging respected.",
  lister: (params) => api.lister("spare-parts", params),
  creer: (data) => api.creer("spare-parts", data),
  modifier: (id, data) => api.modifier("spare-parts", id, data),
  unicite: "code_piece",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_piece", "Code piece", "Part code"),
    col("designation", "Designation", "Description"),
    col("referencence_constructeur", "Ref. constructeur", "Manufacturer ref"),
    col("famille", "Famille", "Family"),
    col("stock_actuel", "Stock actuel", "Current stock"),
    col("seuil_mini", "Seuil mini", "Min threshold"),
    col("prix_unitaire_xaf", "Prix unitaire", "Unit price"),
    col("fournisseur_principal", "Fournisseur principal", "Main supplier"),
    col("compatibilites", "Compatibilites", "Compatibilities"),
  ],
  champs: [
    txt("code_piece", "Code piece", "Part code", { requisCreation: true }),
    txt("designation", "Designation", "Description"),
    txt("referencence_constructeur", "Ref. constructeur", "Manufacturer ref"),
    sel("famille", "Famille", "Family", "famille"),
    num("stock_actuel", "Stock actuel", "Current stock"),
    num("seuil_mini", "Seuil mini", "Min threshold"),
    num("prix_unitaire_xaf", "Prix unitaire", "Unit price"),
    txt("fournisseur_principal", "Fournisseur principal", "Main supplier"),
    txt("compatibilites", "Compatibilites", "Compatibilities"),
  ],
};


export const registreWorkshopAppointment: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "workshop_scheduling",
  tcode: "registre-workshop-scheduling",
  icon: Icons.Calendar,
  titre: "Planification atelier",
  titreEn: "Workshop scheduling",
  description: "RDV maintenance et reparation.",
  descriptionEn: "Maintenance and repair appointments.",
  aide: "Creneau par mecanicien et par pont.",
  aideEn: "Slot per mechanic and lift.",
  lister: (params) => api.lister("workshop-appointments", params),
  creer: (data) => api.creer("workshop-appointments", data),
  modifier: (id, data) => api.modifier("workshop-appointments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("date_horaire", "Date heure", "Date time"),
    col("type_intervention", "Type", "Type"),
    col("mecanicien", "Mecanicien", "Mechanic"),
    col("duree_estimee_h", "Duree estimee (h)", "Est. duration (h)"),
    col("cout_estime_xaf", "Cout estime", "Estimated cost"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    dtx("date_horaire", "Date heure", "Date time"),
    sel("type_intervention", "Type", "Type", "type_intervention"),
    txt("mecanicien", "Mecanicien", "Mechanic"),
    num("duree_estimee_h", "Duree estimee (h)", "Est. duration (h)"),
    num("cout_estime_xaf", "Cout estime", "Estimated cost"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreInsuranceClaim: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "insurance_claim",
  tcode: "registre-insurance-claims",
  icon: Icons.ClipboardList,
  titre: "Sinistres et assurances",
  titreEn: "Insurance claims",
  description: "Declaration sinistre, suivi indemnisation.",
  descriptionEn: "Loss declaration and compensation tracking.",
  aide: "Delai de declaration contractuel strict.",
  aideEn: "Contractual declaration deadline strict.",
  lister: (params) => api.lister("insurance-claims", params),
  creer: (data) => api.creer("insurance-claims", data),
  modifier: (id, data) => api.modifier("insurance-claims", id, data),
  unicite: "numero_sinistre",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_sinistre", "Numero sinistre", "Claim number"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("date_sinistre", "Date sinistre", "Incident date"),
    col("type_sinistre", "Type", "Type"),
    col("description", "Description", "Description"),
    col("montant_estime_xaf", "Montant estime", "Estimated amount"),
    col("montant_indemnise_xaf", "Montant indemnise", "Compensation amount"),
    col("assureur", "Assureur", "Insurer"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_sinistre", "Numero sinistre", "Claim number", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    dt("date_sinistre", "Date sinistre", "Incident date"),
    sel("type_sinistre", "Type", "Type", "type_sinistre"),
    txt("description", "Description", "Description"),
    num("montant_estime_xaf", "Montant estime", "Estimated amount"),
    num("montant_indemnise_xaf", "Montant indemnise", "Compensation amount"),
    txt("assureur", "Assureur", "Insurer"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreRegistrationRecord: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "registration_tracking",
  tcode: "registre-registration-tracking",
  icon: Icons.Contact,
  titre: "Suivi immatriculation",
  titreEn: "Registration tracking",
  description: "Documents officiels d'immatriculation.",
  descriptionEn: "Official registration documents.",
  aide: "Renouvellement 30j avant expiration.",
  aideEn: "Renew 30d before expiry.",
  lister: (params) => api.lister("registration-records", params),
  creer: (data) => api.creer("registration-records", data),
  modifier: (id, data) => api.modifier("registration-records", id, data),
  unicite: "numero_immatriculation",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_immatriculation", "Immatriculation", "Plate"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("proprietaire", "Proprietaire", "Owner"),
    col("date_emission", "Date emission", "Issue date"),
    col("date_expiration", "Date expiration", "Expiry date"),
    col("autorite", "Autorite", "Authority"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_immatriculation", "Immatriculation", "Plate", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    txt("proprietaire", "Proprietaire", "Owner"),
    dt("date_emission", "Date emission", "Issue date"),
    dt("date_expiration", "Date expiration", "Expiry date"),
    txt("autorite", "Autorite", "Authority"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreTechnicalVisit: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "technical_visit",
  tcode: "registre-technical-visits",
  icon: Icons.ClipboardCheck,
  titre: "Visites techniques periodiques",
  titreEn: "Periodic technical inspections",
  description: "Controles techniques obligatoires.",
  descriptionEn: "Mandatory technical inspections.",
  aide: "Report = immobilisation du vehicule.",
  aideEn: "Failure = vehicle immobilized.",
  lister: (params) => api.lister("technical-visits", params),
  creer: (data) => api.creer("technical-visits", data),
  modifier: (id, data) => api.modifier("technical-visits", id, data),
  unicite: "numero_pv",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_pv", "Numero PV", "Report number"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("date_visite", "Date visite", "Inspection date"),
    col("centre_controle", "Centre controle", "Inspection center"),
    col("resultat", "Resultat", "Result"),
    col("observations", "Observations", "Observations"),
    col("contre_visite_possible", "Contre-visite possible", "Retest allowed"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_pv", "Numero PV", "Report number", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    dt("date_visite", "Date visite", "Inspection date"),
    txt("centre_controle", "Centre controle", "Inspection center"),
    sel("resultat", "Resultat", "Result", "resultat"),
    txt("observations", "Observations", "Observations"),
    chk("contre_visite_possible", "Contre-visite possible", "Retest allowed"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreFuelConsumption: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "fuel_consumption",
  tcode: "registre-fuel-consumption",
  icon: Icons.Fuel,
  titre: "Consommation par vehicule",
  titreEn: "Per-vehicle fuel consumption",
  description: "Relevés pleins et consommation moyenne.",
  descriptionEn: "Fuel ups and average consumption.",
  aide: "Ecart > 15% declenche investigation.",
  aideEn: "Gap > 15% triggers investigation.",
  lister: (params) => api.lister("fuel-consumptions", params),
  creer: (data) => api.creer("fuel-consumptions", data),
  modifier: (id, data) => api.modifier("fuel-consumptions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("date", "Date", "Date"),
    col("litres", "Litres", "Litres"),
    col("prix_total_xaf", "Prix total", "Total cost"),
    col("km_etape", "Km etape", "Stage km"),
    col("conso_l100km", "Conso (L/100km)", "Consumption (L/100km)"),
    col("station", "Station", "Station"),
    col("carburant", "Carburant", "Fuel type"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    dt("date", "Date", "Date"),
    num("litres", "Litres", "Litres"),
    num("prix_total_xaf", "Prix total", "Total cost"),
    num("km_etape", "Km etape", "Stage km"),
    num("conso_l100km", "Conso (L/100km)", "Consumption (L/100km)"),
    txt("station", "Station", "Station"),
    sel("carburant", "Carburant", "Fuel type", "carburant"),
  ],
};


export const registreVehicleLifecycle: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "vehicle_lifecycle",
  tcode: "registre-vehicle-lifecycle",
  icon: Icons.Recycle,
  titre: "Cycle de vie / reforme",
  titreEn: "Vehicle lifecycle / decommission",
  description: "Etapes de la vie du vehicule.",
  descriptionEn: "Life stages of the vehicle.",
  aide: "Reforme validee par DAF et direction technique.",
  aideEn: "Disposal approved by CFO and technical direction.",
  lister: (params) => api.lister("vehicle-lifecycles", params),
  creer: (data) => api.creer("vehicle-lifecycles", data),
  modifier: (id, data) => api.modifier("vehicle-lifecycles", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("date_acquisition", "Acquisition", "Acquisition"),
    col("date_reforme", "Reforme", "Decommission"),
    col("duree_detention_an", "Duree detention (an)", "Ownership (y)"),
    col("km_final", "Km final", "Final km"),
    col("mode_reforme", "Mode reforme", "Disposal mode"),
    col("valeur_recuperation_xaf", "Valeur recuperation", "Recovery value"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    dt("date_acquisition", "Acquisition", "Acquisition"),
    dt("date_reforme", "Reforme", "Decommission"),
    num("duree_detention_an", "Duree detention (an)", "Ownership (y)"),
    num("km_final", "Km final", "Final km"),
    sel("mode_reforme", "Mode reforme", "Disposal mode", "mode_reforme"),
    num("valeur_recuperation_xaf", "Valeur recuperation", "Recovery value"),
  ],
};


export const registreCostAnalysis: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "cost_analysis",
  tcode: "registre-cost-analysis",
  icon: Icons.BarChart,
  titre: "Analyse couts par vehicule",
  titreEn: "Cost analysis per vehicle",
  description: "Couts par periode et par poste.",
  descriptionEn: "Costs per period and line item.",
  aide: "Indispensable pour le pilotage du TCO.",
  aideEn: "Essential for TCO steering.",
  lister: (params) => api.lister("cost-analyses", params),
  creer: (data) => api.creer("cost-analyses", data),
  modifier: (id, data) => api.modifier("cost-analyses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("periode", "Periode", "Period"),
    col("cout_carburant_xaf", "Carburant", "Fuel"),
    col("cout_maintenance_xaf", "Maintenance", "Maintenance"),
    col("cout_assurance_xaf", "Assurance", "Insurance"),
    col("cout_amortissement_xaf", "Amortissement", "Depreciation"),
    col("cout_total_xaf", "Cout total", "Total cost"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    txt("periode", "Periode", "Period"),
    num("cout_carburant_xaf", "Carburant", "Fuel"),
    num("cout_maintenance_xaf", "Maintenance", "Maintenance"),
    num("cout_assurance_xaf", "Assurance", "Insurance"),
    num("cout_amortissement_xaf", "Amortissement", "Depreciation"),
    num("cout_total_xaf", "Cout total", "Total cost"),
  ],
};

