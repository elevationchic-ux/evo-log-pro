/**
 * Configs Registre pour convoi-exceptionnel (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("convoi-exceptionnel");

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

export const registreHeavy2LiftPlan: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "lift_plan",
  tcode: "registre-lifting-procedures",
  icon: Icons.MoveVertical,
  titre: "Plans de levage",
  titreEn: "Lift plans",
  description: "Plan technique de levage d' une charge lourde.",
  descriptionEn: "Technical plan for lifting a heavy load.",
  aide: "La capacite de la grue doit couvrir le poids + acces.",
  aideEn: "Crane capacity must cover weight plus radius.",
  lister: (params) => api.lister("heavy2-lift-plans", params),
  creer: (data) => api.creer("heavy2-lift-plans", data),
  modifier: (id, data) => api.modifier("heavy2-lift-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("charge", "Charge", "Load"),
    col("poids_tonnes", "Poids (t)", "Weight (t)"),
    col("portee_m", "Portee (m)", "Radius (m)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("charge", "Charge", "Load"),
    num("poids_tonnes", "Poids (t)", "Weight (t)"),
    num("portee_m", "Portee (m)", "Radius (m)"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2RouteSurvey: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "route_survey",
  tcode: "registre-route-feasibility",
  icon: Icons.Route,
  titre: "Reconnaissances d' itineraire",
  titreEn: "Route surveys",
  description: "Etude de faisabilite routiere d' un convoi hors gabarit.",
  descriptionEn: "Road feasibility study of an oversize convoy.",
  aide: "Le gabarit et les obstacles conditionnent le passage.",
  aideEn: "Gauge and obstacles condition the passage.",
  lister: (params) => api.lister("heavy2-route-surveys", params),
  creer: (data) => api.creer("heavy2-route-surveys", data),
  modifier: (id, data) => api.modifier("heavy2-route-surveys", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("itineraire", "Itineraire", "Route"),
    col("largeur_m", "Largeur (m)", "Width (m)"),
    col("hauteur_m", "Hauteur (m)", "Height (m)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("itineraire", "Itineraire", "Route"),
    num("largeur_m", "Largeur (m)", "Width (m)"),
    num("hauteur_m", "Hauteur (m)", "Height (m)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2EscortSchedule: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "escort_schedule",
  tcode: "registre-escort-schedules",
  icon: Icons.ShieldCheck,
  titre: "Planning d' escortes",
  titreEn: "Escort schedules",
  description: "Affectation des vehicules d' escorte a un convoi.",
  descriptionEn: "Assignment of escort vehicles to a convoy.",
  aide: "Le nb d' escortes depende du gabarit.",
  aideEn: "Escort count depends on the gauge.",
  lister: (params) => api.lister("heavy2-escort-schedules", params),
  creer: (data) => api.creer("heavy2-escort-schedules", data),
  modifier: (id, data) => api.modifier("heavy2-escort-schedules", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("convoi", "Convoi", "Convoy"),
    col("nb_vehicules", "Nb vehicules", "Vehicles"),
    col("debut", "Debut", "Start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("convoi", "Convoi", "Convoy"),
    num("nb_vehicules", "Nb vehicules", "Vehicles"),
    dtx("debut", "Debut", "Start"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2LoadMomentCalc: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "load_moment_calc",
  tcode: "registre-load-moment-calcs",
  icon: Icons.Scale,
  titre: "Calculs de moment de charge",
  titreEn: "Load moment calcs",
  description: "Calcul du moment de renversement d' une configuration de levage.",
  descriptionEn: "Calculation of the overturning moment of a lift setup.",
  aide: "Le moment applique ne doit pas exceder la capacite.",
  aideEn: "The applied moment must not exceed capacity.",
  lister: (params) => api.lister("heavy2-load-moment-calcs", params),
  creer: (data) => api.creer("heavy2-load-moment-calcs", data),
  modifier: (id, data) => api.modifier("heavy2-load-moment-calcs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("configuration", "Configuration", "Configuration"),
    col("moment_applique", "Moment applique", "Applied moment"),
    col("capacite", "Capacite", "Capacity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("configuration", "Configuration", "Configuration"),
    num("moment_applique", "Moment applique", "Applied moment"),
    num("capacite", "Capacite", "Capacity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2CraneSetupRecord: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "crane_setup_record",
  tcode: "registre-crane-setup-records",
  icon: Icons.Cog,
  titre: "Montages de grue",
  titreEn: "Crane setup records",
  description: "Enregistrement du montage et calage d' une grue.",
  descriptionEn: "Record of a crane's assembly and leveling.",
  aide: "Le calage et le sol porteur valident le montage.",
  aideEn: "Leveling and ground bearing validate the setup.",
  lister: (params) => api.lister("heavy2-crane-setup-records", params),
  creer: (data) => api.creer("heavy2-crane-setup-records", data),
  modifier: (id, data) => api.modifier("heavy2-crane-setup-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("grue", "Grue", "Crane"),
    col("portance_sol", "Portance du sol", "Ground bearing"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("grue", "Grue", "Crane"),
    txt("portance_sol", "Portance du sol", "Ground bearing"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2PermitObtention: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "permit_obtention",
  tcode: "registre-permit-obtentions",
  icon: Icons.FileBadge,
  titre: "Obtentions d' autorisation",
  titreEn: "Permit obtentions",
  description: "Demande et obtaining du permis de transport exceptionnel.",
  descriptionEn: "Application and obtaining of the oversize transport permit.",
  aide: "Le parcours et les autorites traversees encadrent le permis.",
  aideEn: "Route and crossed authorities bound the permit.",
  lister: (params) => api.lister("heavy2-permit-obtentions", params),
  creer: (data) => api.creer("heavy2-permit-obtentions", data),
  modifier: (id, data) => api.modifier("heavy2-permit-obtentions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("convoi", "Convoi", "Convoy"),
    col("autorite", "Autorite", "Authority"),
    col("validite", "Validite", "Validity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("convoi", "Convoi", "Convoy"),
    txt("autorite", "Autorite", "Authority"),
    dt("validite", "Validite", "Validity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2LashingRig: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "lashing_rig",
  tcode: "registre-lashing-rigs",
  icon: Icons.Anchor,
  titre: "Dispositifs d' arrimage",
  titreEn: "Lashing rigs",
  description: "Configuration d' arrimage d' une charge sur son support.",
  descriptionEn: "Rigging configuration of a load on its carrier.",
  aide: "Le nombre de sangles et l' angle valident l' arrimage.",
  aideEn: "Strap count and angle validate the lashing.",
  lister: (params) => api.lister("heavy2-lashing-rigs", params),
  creer: (data) => api.creer("heavy2-lashing-rigs", data),
  modifier: (id, data) => api.modifier("heavy2-lashing-rigs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("charge", "Charge", "Load"),
    col("nb_sangles", "Nb sangles", "Straps"),
    col("angle_deg", "Angle (deg)", "Angle (deg)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("charge", "Charge", "Load"),
    num("nb_sangles", "Nb sangles", "Straps"),
    num("angle_deg", "Angle (deg)", "Angle (deg)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2AxleLoadReading: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "axle_load_reading",
  tcode: "registre-axle-load-readings",
  icon: Icons.Weight,
  titre: "Releves de charge par essieu",
  titreEn: "Axle load readings",
  description: "Mesure de la charge reposee par essieu du porte-engin.",
  descriptionEn: "Measurement of the weight borne per trailer axle.",
  aide: "La charge par essieu ne doit pas depasser la limite legale.",
  aideEn: "Per-axle load must not exceed the legal limit.",
  lister: (params) => api.lister("heavy2-axle-load-readings", params),
  creer: (data) => api.creer("heavy2-axle-load-readings", data),
  modifier: (id, data) => api.modifier("heavy2-axle-load-readings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("essieu", "Essieu", "Axle"),
    col("charge_t", "Charge (t)", "Load (t)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    num("essieu", "Essieu", "Axle"),
    num("charge_t", "Charge (t)", "Load (t)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHeavy2ConvoyStagingReport: ConfigRegistre = {
  permModule: "heavylift",
  permSousModule: "convoy_staging_report",
  tcode: "registre-convoy-staging-reports",
  icon: Icons.Truck,
  titre: "Comptes-rendus de rassemblement",
  titreEn: "Convoy staging reports",
  description: "Bilan du rassemblement et du depart d' un convoi.",
  descriptionEn: "Summary of a convoy's assembly and departure.",
  aide: "Le respect du creneau de depart evite les blocages reseau.",
  aideEn: "Keeping the departure slot avoids network blockages.",
  lister: (params) => api.lister("heavy2-convoy-staging-reports", params),
  creer: (data) => api.creer("heavy2-convoy-staging-reports", data),
  modifier: (id, data) => api.modifier("heavy2-convoy-staging-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("convoi", "Convoi", "Convoy"),
    col("lieu_rassemblement", "Lieu de rassemblement", "Staging place"),
    col("depart", "Depart", "Departure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("convoi", "Convoi", "Convoy"),
    txt("lieu_rassemblement", "Lieu de rassemblement", "Staging place"),
    dtx("depart", "Depart", "Departure"),
    txt("statut", "Statut", "Status"),
  ],
};

