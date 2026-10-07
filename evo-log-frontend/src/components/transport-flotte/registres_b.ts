/**
 * Configs Registre pour transport-flotte (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("transport-flotte");

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

export const registreTransportbDispatch: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "dispatch",
  tcode: "registre-mission-dispatches",
  icon: Icons.Navigation,
  titre: "Bons de mission / affectation",
  titreEn: "Mission dispatches",
  description: "Affectation d'un vehicule et d'un chauffeur a une mission de transport.",
  descriptionEn: "Assignment of a vehicle and driver to a transport mission.",
  aide: "Distance reellement parcourue vs previsonnelle.",
  aideEn: "Actual distance vs planned.",
  lister: (params) => api.lister("transportb-dispatches", params),
  creer: (data) => api.creer("transportb-dispatches", data),
  modifier: (id, data) => api.modifier("transportb-dispatches", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference mission", "Mission reference"),
    col("chauffeur", "Chauffeur", "Driver"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("point_depart", "Point de depart", "Pickup point"),
    col("point_arrivee", "Point d'arrivee", "Drop-off point"),
    col("date_depart", "Depart", "Departure"),
    col("date_arrivee", "Arrivee", "Arrival"),
    col("km_parcourus", "Km parcourus", "Km driven"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference mission", "Mission reference", { requisCreation: true }),
    txt("chauffeur", "Chauffeur", "Driver"),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("point_depart", "Point de depart", "Pickup point"),
    txt("point_arrivee", "Point d'arrivee", "Drop-off point"),
    dtx("date_depart", "Depart", "Departure"),
    dtx("date_arrivee", "Arrivee", "Arrival"),
    num("km_parcourus", "Km parcourus", "Km driven"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTransportbPod: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "pod",
  tcode: "registre-proof-of-delivery",
  icon: Icons.FileSignature,
  titre: "Preuves de livraison (POD)",
  titreEn: "Proof of delivery",
  description: "Accuse de livraison signe par le destinataire.",
  descriptionEn: "Delivery receipt signed by the consignee.",
  aide: "Signature et nombre de colis livres font foi de la livraison.",
  aideEn: "Signature and delivered parcel count prove the delivery.",
  lister: (params) => api.lister("transportb-proof-delivery", params),
  creer: (data) => api.creer("transportb-proof-delivery", data),
  modifier: (id, data) => api.modifier("transportb-proof-delivery", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference POD", "POD reference"),
    col("mission", "Mission", "Mission"),
    col("destinataire", "Destinataire", "Consignee"),
    col("date_livraison", "Date livraison", "Delivery date"),
    col("nb_colis_livres", "Colis livres", "Parcels delivered"),
    col("incidents", "Incidents", "Incidents"),
    col("signature_recu", "Signature recue", "Signature received"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference POD", "POD reference", { requisCreation: true }),
    txt("mission", "Mission", "Mission"),
    txt("destinataire", "Destinataire", "Consignee"),
    dtx("date_livraison", "Date livraison", "Delivery date"),
    num("nb_colis_livres", "Colis livres", "Parcels delivered"),
    txt("incidents", "Incidents", "Incidents"),
    chk("signature_recu", "Signature recue", "Signature received"),
    txt("statut", "Statut", "Status"),
  ],
};

