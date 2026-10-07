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

export const registreParcDriverAssignment: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "driver_assignment",
  tcode: "registre-driver-assignments",
  icon: Icons.UserCheck,
  titre: "Affectation chauffeurs",
  titreEn: "Driver assignments",
  description: "Affectation chauffeur / vehicule par periode.",
  descriptionEn: "Driver / vehicle assignment per period.",
  aide: "Controle permis et temps de conduite.",
  aideEn: "License and driving-time check.",
  lister: (params) => api.lister("parcb-driver-assignments", params),
  creer: (data) => api.creer("parcb-driver-assignments", data),
  modifier: (id, data) => api.modifier("parcb-driver-assignments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference affectation", "Assignment reference"),
    col("immatriculation", "Immatriculation", "Plate"),
    col("chauffeur", "Chauffeur", "Driver"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("kilometrage_debut", "Km debut", "Start odometer"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference affectation", "Assignment reference", { requisCreation: true }),
    txt("immatriculation", "Immatriculation", "Plate"),
    txt("chauffeur", "Chauffeur", "Driver"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    num("kilometrage_debut", "Km debut", "Start odometer"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreParcGeofenceZone: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "geofence_zone",
  tcode: "registre-geofence-zones",
  icon: Icons.MapPin,
  titre: "Zones geoclotees",
  titreEn: "Geofence zones",
  description: "Perimetres virtuels declenchant des alertes de sortie.",
  descriptionEn: "Virtual boundaries triggering exit alerts.",
  aide: "Base des alertes GPS hors zone.",
  aideEn: "Basis of out-of-zone GPS alerts.",
  lister: (params) => api.lister("parcb-geofence-zones", params),
  creer: (data) => api.creer("parcb-geofence-zones", data),
  modifier: (id, data) => api.modifier("parcb-geofence-zones", id, data),
  unicite: "code_zone",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_zone", "Code zone", "Zone code"),
    col("nom_zone", "Nom zone", "Zone name"),
    col("centre_lat", "Centre lat", "Center lat"),
    col("centre_lng", "Centre lng", "Center lng"),
    col("rayon_m", "Rayon (m)", "Radius (m)"),
    col("alerte_sortie", "Alerte sortie", "Exit alert"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_zone", "Code zone", "Zone code", { requisCreation: true }),
    txt("nom_zone", "Nom zone", "Zone name"),
    txt("centre_lat", "Centre lat", "Center lat"),
    txt("centre_lng", "Centre lng", "Center lng"),
    num("rayon_m", "Rayon (m)", "Radius (m)"),
    chk("alerte_sortie", "Alerte sortie", "Exit alert"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreParcInspectionChecklist: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "inspection_checklist",
  tcode: "registre-inspection-checklists",
  icon: Icons.CheckSquare,
  titre: "Checklists de controle",
  titreEn: "Inspection checklists",
  description: "Controles avant depart (exterieur, interieur, securite).",
  descriptionEn: "Pre-trip checks (exterior, interior, safety).",
  aide: "Anomalie bloquante = immobilisation.",
  aideEn: "Blocking anomaly = immobilization.",
  lister: (params) => api.lister("parcb-inspection-checklists", params),
  creer: (data) => api.creer("parcb-inspection-checklists", data),
  modifier: (id, data) => api.modifier("parcb-inspection-checklists", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference controle", "Checklist reference"),
    col("immatriculation", "Immatriculation", "Plate"),
    col("chauffeur", "Chauffeur", "Driver"),
    col("date_controle", "Date controle", "Check date"),
    col("points_controles", "Points controles", "Points checked"),
    col("anomalies_nb", "Anomalies", "Anomalies count"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference controle", "Checklist reference", { requisCreation: true }),
    txt("immatriculation", "Immatriculation", "Plate"),
    txt("chauffeur", "Chauffeur", "Driver"),
    dtx("date_controle", "Date controle", "Check date"),
    num("points_controles", "Points controles", "Points checked"),
    num("anomalies_nb", "Anomalies", "Anomalies count"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreParcLeaseContract: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "lease_contract",
  tcode: "registre-lease-contracts",
  icon: Icons.FileSignature,
  titre: "Contrats de location / leasing",
  titreEn: "Lease contracts",
  description: "Contrats de location longue duree de vehicules.",
  descriptionEn: "Long-term vehicle leasing agreements.",
  aide: "Suivi loyer, echeance et restitution.",
  aideEn: "Tracks rent, term and return.",
  lister: (params) => api.lister("parcb-lease-contracts", params),
  creer: (data) => api.creer("parcb-lease-contracts", data),
  modifier: (id, data) => api.modifier("parcb-lease-contracts", id, data),
  unicite: "numero_contrat",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_contrat", "Numero contrat", "Contract number"),
    col("loueur", "Loueur", "Lessor"),
    col("immatriculation", "Immatriculation", "Plate"),
    col("loyer_mensuel_xaf", "Loyer mensuel (XAF)", "Monthly rent (XAF)"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_contrat", "Numero contrat", "Contract number", { requisCreation: true }),
    txt("loueur", "Loueur", "Lessor"),
    txt("immatriculation", "Immatriculation", "Plate"),
    num("loyer_mensuel_xaf", "Loyer mensuel (XAF)", "Monthly rent (XAF)"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreParcTollPass: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "toll_pass",
  tcode: "registre-toll-passes",
  icon: Icons.Ticket,
  titre: "Badges de peage / telepeage",
  titreEn: "Toll passes",
  description: "Affectation des badges de telepeage aux vehicules.",
  descriptionEn: "Assignment of toll tags to vehicles.",
  aide: "Solde recharge ; alerte si vide.",
  aideEn: "Prepaid balance; alert when empty.",
  lister: (params) => api.lister("parcb-toll-passes", params),
  creer: (data) => api.creer("parcb-toll-passes", data),
  modifier: (id, data) => api.modifier("parcb-toll-passes", id, data),
  unicite: "numero_badge",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_badge", "Numero badge", "Badge number"),
    col("immatriculation", "Immatriculation", "Plate"),
    col("operateur", "Operateur", "Operator"),
    col("solde_xaf", "Solde (XAF)", "Balance (XAF)"),
    col("date_expiration", "Expiration", "Expiry date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_badge", "Numero badge", "Badge number", { requisCreation: true }),
    txt("immatriculation", "Immatriculation", "Plate"),
    txt("operateur", "Operateur", "Operator"),
    num("solde_xaf", "Solde (XAF)", "Balance (XAF)"),
    dt("date_expiration", "Expiration", "Expiry date"),
    txt("statut", "Statut", "Status"),
  ],
};

