/**
 * Configs Registre pour port-operations (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("port-operations");

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

export const registrePortbBerthSchedule: ConfigRegistre = {
  permModule: "port",
  permSousModule: "berth_schedule",
  tcode: "registre-berth-schedules",
  icon: Icons.Anchor,
  titre: "Plans d'escale et postes d'amarrage",
  titreEn: "Berth schedules",
  description: "Affectation d'un poste d'amarrage et d'un creneau a un navire.",
  descriptionEn: "Assignment of a berth and time window to a vessel.",
  aide: "Un poste par creneau ; conflits de quais a eviter.",
  aideEn: "One berth per slot; avoid quay conflicts.",
  lister: (params) => api.lister("portb-berth-schedules", params),
  creer: (data) => api.creer("portb-berth-schedules", data),
  modifier: (id, data) => api.modifier("portb-berth-schedules", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference escale", "Call reference"),
    col("navire", "Navire", "Vessel"),
    col("numero_imo", "Numero IMO", "IMO number"),
    col("poste_amarrage", "Poste d'amarrage", "Berth"),
    col("date_arrivee_prevue", "ETA", "ETA"),
    col("date_depart_prevu", "ETD", "ETD"),
    col("type_cargo", "Type de cargo", "Cargo type"),
    col("pilote", "Pilote", "Pilot"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference escale", "Call reference", { requisCreation: true }),
    txt("navire", "Navire", "Vessel"),
    txt("numero_imo", "Numero IMO", "IMO number"),
    txt("poste_amarrage", "Poste d'amarrage", "Berth"),
    dtx("date_arrivee_prevue", "ETA", "ETA"),
    dtx("date_depart_prevu", "ETD", "ETD"),
    txt("type_cargo", "Type de cargo", "Cargo type"),
    txt("pilote", "Pilote", "Pilot"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePortbVesselTrafficLog: ConfigRegistre = {
  permModule: "port",
  permSousModule: "vessel_traffic_log",
  tcode: "registre-vessel-traffic-logs",
  icon: Icons.Ship,
  titre: "Journal de trafic maritime (VTS)",
  titreEn: "Vessel traffic logs",
  description: "Enregistrement des mouvements de navires dans la zone VTS.",
  descriptionEn: "Record of vessel movements within the VTS area.",
  aide: "Chaque mouvement est horodate et verifie par l'operateur VTS.",
  aideEn: "Each movement is timestamped and checked by the VTS operator.",
  lister: (params) => api.lister("portb-vessel-traffic-logs", params),
  creer: (data) => api.creer("portb-vessel-traffic-logs", data),
  modifier: (id, data) => api.modifier("portb-vessel-traffic-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference mouvement", "Movement reference"),
    col("nom_navire", "Nom du navire", "Vessel name"),
    col("numero_imo", "Numero IMO", "IMO number"),
    col("mouvement", "Mouvement", "Movement"),
    col("balise_vts", "Balise VTS", "VTS beacon"),
    col("horodatage", "Horodatage", "Timestamp"),
    col("operateur", "Operateur", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference mouvement", "Movement reference", { requisCreation: true }),
    txt("nom_navire", "Nom du navire", "Vessel name"),
    txt("numero_imo", "Numero IMO", "IMO number"),
    txt("mouvement", "Mouvement", "Movement"),
    txt("balise_vts", "Balise VTS", "VTS beacon"),
    dtx("horodatage", "Horodatage", "Timestamp"),
    txt("operateur", "Operateur", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};

