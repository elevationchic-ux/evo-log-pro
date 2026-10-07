/**
 * Configs Registre pour courier-express (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("courier-express");

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

export const registreCour2RouteScan: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "route_scan",
  tcode: "registre-route-scans",
  icon: Icons.ScanLine,
  titre: "Scans de tournee",
  titreEn: "Route scans",
  description: "Scan d' un colis realise aux etapes de la tournee.",
  descriptionEn: "Parcel scan performed along the route steps.",
  aide: "L' horodatage de scan trace la chaine de possession.",
  aideEn: "The scan timestamp traces the chain of custody.",
  lister: (params) => api.lister("cour2-route-scans", params),
  creer: (data) => api.creer("cour2-route-scans", data),
  modifier: (id, data) => api.modifier("cour2-route-scans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("colis", "Colis", "Parcel"),
    col("etape", "Etape", "Step"),
    col("lieu", "Lieu", "Location"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("colis", "Colis", "Parcel"),
    txt("etape", "Etape", "Step"),
    txt("lieu", "Lieu", "Location"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCour2LastMileHandoff: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "last_mile_handoff",
  tcode: "registre-last-mile-handoffs",
  icon: Icons.Package,
  titre: "Remises dernier kilometre",
  titreEn: "Last-mile handoffs",
  description: "Passation d' un colis au livreur dernier kilometre.",
  descriptionEn: "Handover of a parcel to the last-mile courier.",
  aide: "La remise au livreur engage sa responsabilite.",
  aideEn: "The handover to the courier commits his responsibility.",
  lister: (params) => api.lister("cour2-last-mile-handoffs", params),
  creer: (data) => api.creer("cour2-last-mile-handoffs", data),
  modifier: (id, data) => api.modifier("cour2-last-mile-handoffs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("colis", "Colis", "Parcel"),
    col("livreur", "Livreur", "Courier"),
    col("agencer", "Agence", "Hub"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("colis", "Colis", "Parcel"),
    txt("livreur", "Livreur", "Courier"),
    txt("agencer", "Agence", "Hub"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCour2DeliveryAttempt: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "delivery_attempt",
  tcode: "registre-delivery-attempts",
  icon: Icons.MapPin,
  titre: "Tentatives de livraison",
  titreEn: "Delivery attempts",
  description: "Chaque passage du livreur au point de livraison.",
  descriptionEn: "Each courier stop at the delivery point.",
  aide: "Le motif d' echec justifie la nouvelle presentation.",
  aideEn: "The failure reason justifies re-presentation.",
  lister: (params) => api.lister("cour2-delivery-attempts", params),
  creer: (data) => api.creer("cour2-delivery-attempts", data),
  modifier: (id, data) => api.modifier("cour2-delivery-attempts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("colis", "Colis", "Parcel"),
    col("livreur", "Livreur", "Courier"),
    col("date", "Date", "Date"),
    col("motif", "Motif", "Outcome"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("colis", "Colis", "Parcel"),
    txt("livreur", "Livreur", "Courier"),
    dtx("date", "Date", "Date"),
    txt("motif", "Motif", "Outcome"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCour2ExceptionParcel: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "exception_parcel",
  tcode: "registre-exception-parcels",
  icon: Icons.FileWarning,
  titre: "Colis en exception",
  titreEn: "Exception parcels",
  description: "Colis bloque par une anomalie de traitement.",
  descriptionEn: "Parcel blocked by a handling anomaly.",
  aide: "La classification de l' exception pilote la resolution.",
  aideEn: "Exception classification drives resolution.",
  lister: (params) => api.lister("cour2-exception-parcels", params),
  creer: (data) => api.creer("cour2-exception-parcels", data),
  modifier: (id, data) => api.modifier("cour2-exception-parcels", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("colis", "Colis", "Parcel"),
    col("type_exception", "Type", "Exception type"),
    col("detecte_le", "Detecte le", "Detected at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("colis", "Colis", "Parcel"),
    txt("type_exception", "Type", "Exception type"),
    dtx("detecte_le", "Detecte le", "Detected at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCour2ReturnToSender: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "return_to_sender",
  tcode: "registre-returns-to-sender",
  icon: Icons.Send,
  titre: "Retours expediteur",
  titreEn: "Returns to sender",
  description: "Reexpedition d' un colis non livre a son expediteur.",
  descriptionEn: "Re-dispatch of an undelivered parcel to its sender.",
  aide: "Le motif et le trajet de retour encadrent le litige.",
  aideEn: "The reason and return route bound the dispute.",
  lister: (params) => api.lister("cour2-returns-to-sender", params),
  creer: (data) => api.creer("cour2-returns-to-sender", data),
  modifier: (id, data) => api.modifier("cour2-returns-to-sender", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("colis", "Colis", "Parcel"),
    col("motif", "Motif", "Reason"),
    col("date_depart", "Depart", "Departure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("colis", "Colis", "Parcel"),
    txt("motif", "Motif", "Reason"),
    dtx("date_depart", "Depart", "Departure"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCour2CourierShiftLog: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "courier_shift_log",
  tcode: "registre-courier-shift-logs",
  icon: Icons.ClipboardList,
  titre: "Journal de vacation livreur",
  titreEn: "Courier shift logs",
  description: "Suivi de vacation et de tournee d' un livreur.",
  descriptionEn: "Tracking of a courier's shift and route.",
  aide: "Le nombre de colis livres mesure la productivite.",
  aideEn: "Parcels delivered measures productivity.",
  lister: (params) => api.lister("cour2-courier-shift-logs", params),
  creer: (data) => api.creer("cour2-courier-shift-logs", data),
  modifier: (id, data) => api.modifier("cour2-courier-shift-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("livreur", "Livreur", "Courier"),
    col("date", "Date", "Date"),
    col("colis_livres", "Colis livres", "Delivered"),
    col("km", "Kilometres", "Kilometers"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("livreur", "Livreur", "Courier"),
    dt("date", "Date", "Date"),
    num("colis_livres", "Colis livres", "Delivered"),
    num("km", "Kilometres", "Kilometers"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCour2SlaBreachLog: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "sla_breach_log",
  tcode: "registre-sla-breach-logs",
  icon: Icons.Timer,
  titre: "Journaux de rupture SLA",
  titreEn: "SLA breach logs",
  description: "Constat de depassement de l' engagement de delai.",
  descriptionEn: "Record of a missed delivery-time commitment.",
  aide: "Le retard et la compensation associee engagent le client.",
  aideEn: "The delay and compensation commit the account.",
  lister: (params) => api.lister("cour2-sla-breach-logs", params),
  creer: (data) => api.creer("cour2-sla-breach-logs", data),
  modifier: (id, data) => api.modifier("cour2-sla-breach-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("colis", "Colis", "Parcel"),
    col("retard_min", "Retard (min)", "Delay (min)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("colis", "Colis", "Parcel"),
    num("retard_min", "Retard (min)", "Delay (min)"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

