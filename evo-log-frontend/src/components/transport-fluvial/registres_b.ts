/**
 * Configs Registre pour transport-fluvial (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("transport-fluvial");

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

export const registreFluvialCanalSection: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "canal_section",
  tcode: "registre-canal-sections",
  icon: Icons.Route,
  titre: "Sections de voie navigable",
  titreEn: "Canal sections",
  description: "Troncons de voie d eau avec cotes, biefs et restrictions.",
  descriptionEn: "Waterway reaches with gauges, locks and restrictions.",
  aide: "Base du calcul de tirant d eau pratique.",
  aideEn: "Basis of practical draft calc.",
  lister: (params) => api.lister("fluvb-canal-sections", params),
  creer: (data) => api.creer("fluvb-canal-sections", data),
  modifier: (id, data) => api.modifier("fluvb-canal-sections", id, data),
  unicite: "code_section",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_section", "Code section", "Section code"),
    col("nom_bief", "Nom du bief", "Reach name"),
    col("longueur_km", "Longueur (km)", "Length (km)"),
    col("nb_ecluses", "Nb ecluses", "Locks"),
    col("gabarit_max_t", "Gabarit max (t)", "Max gauge (t)"),
    col("profondeur_cote_cm", "Profondeur cotee (cm)", "Design depth (cm)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_section", "Code section", "Section code", { requisCreation: true }),
    txt("nom_bief", "Nom du bief", "Reach name"),
    num("longueur_km", "Longueur (km)", "Length (km)"),
    num("nb_ecluses", "Nb ecluses", "Locks"),
    num("gabarit_max_t", "Gabarit max (t)", "Max gauge (t)"),
    num("profondeur_cote_cm", "Profondeur cotee (cm)", "Design depth (cm)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialConvoy: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "convoy",
  tcode: "registre-convoys",
  icon: Icons.Link,
  titre: "Convois pousses",
  titreEn: "Push convoys",
  description: "Attelage pousseur + peniches associees.",
  descriptionEn: "Pusher plus attached barges.",
  aide: "Longueur et masse cumulées controlees.",
  aideEn: "Combined length and mass checked.",
  lister: (params) => api.lister("flvb-convoys", params),
  creer: (data) => api.creer("flvb-convoys", data),
  modifier: (id, data) => api.modifier("flvb-convoys", id, data),
  unicite: "numero_convoi",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_convoi", "Numero convoi", "Convoy number"),
    col("pousseur", "Pousseur", "Pusher"),
    col("nb_peniches", "Nb peniches", "Barges"),
    col("masse_total_t", "Masse totale (t)", "Total mass (t)"),
    col("longueur_total_m", "Longueur totale (m)", "Total length (m)"),
    col("itineraire", "Itineraire", "Route"),
    col("date_depart", "Date depart", "Departure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_convoi", "Numero convoi", "Convoy number", { requisCreation: true }),
    txt("pousseur", "Pousseur", "Pusher"),
    num("nb_peniches", "Nb peniches", "Barges"),
    num("masse_total_t", "Masse totale (t)", "Total mass (t)"),
    num("longueur_total_m", "Longueur totale (m)", "Total length (m)"),
    txt("itineraire", "Itineraire", "Route"),
    dtx("date_depart", "Date depart", "Departure"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialBallastOperation: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "ballast_operation",
  tcode: "registre-ballast-operations",
  icon: Icons.Droplets,
  titre: "Lestage / delestage",
  titreEn: "Ballast operations",
  description: "Operations de lestage pour stabilite et tirant d eau.",
  descriptionEn: "Ballasting for stability and draft.",
  aide: "Enregistre masse d eau de lestage.",
  aideEn: "Records ballast water mass.",
  lister: (params) => api.lister("flvb-ballast-operations", params),
  creer: (data) => api.creer("flvb-ballast-operations", data),
  modifier: (id, data) => api.modifier("flvb-ballast-operations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference operation", "Operation reference"),
    col("numero_flotte", "Bateau", "Vessel"),
    col("type_operation", "Type operation", "Operation type"),
    col("masse_balle_t", "Masse lestage (t)", "Ballast mass (t)"),
    col("date_operation", "Date", "Date"),
    col("terminal", "Terminal", "Terminal"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference operation", "Operation reference", { requisCreation: true }),
    txt("numero_flotte", "Bateau", "Vessel"),
    txt("type_operation", "Type operation", "Operation type"),
    num("masse_balle_t", "Masse lestage (t)", "Ballast mass (t)"),
    dtx("date_operation", "Date", "Date"),
    txt("terminal", "Terminal", "Terminal"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialWaterGauge: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "water_gauge",
  tcode: "registre-water-gauges",
  icon: Icons.Waves,
  titre: "Echelles d eau / limnimetres",
  titreEn: "Water level gauges",
  description: "Releves de niveau d eau par poste de mesure.",
  descriptionEn: "Water level readings per gauging station.",
  aide: "Declenche restriction quand cote sous seuil.",
  aideEn: "Triggers restriction below threshold.",
  lister: (params) => api.lister("flvb-water-gauges", params),
  creer: (data) => api.creer("flvb-water-gauges", data),
  modifier: (id, data) => api.modifier("flvb-water-gauges", id, data),
  unicite: "code_poste",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_poste", "Code poste", "Station code"),
    col("nom_poste", "Nom poste", "Station name"),
    col("bief", "Bief", "Reach"),
    col("cote_cm", "Cote (cm)", "Level (cm)"),
    col("cote_seuil_restr_cm", "Seuil restriction (cm)", "Restriction threshold (cm)"),
    col("date_releve", "Date releve", "Reading date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_poste", "Code poste", "Station code", { requisCreation: true }),
    txt("nom_poste", "Nom poste", "Station name"),
    txt("bief", "Bief", "Reach"),
    num("cote_cm", "Cote (cm)", "Level (cm)"),
    num("cote_seuil_restr_cm", "Seuil restriction (cm)", "Restriction threshold (cm)"),
    dtx("date_releve", "Date releve", "Reading date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialBerthingSlot: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "berthing_slot",
  tcode: "registre-berthing-slots",
  icon: Icons.Anchor,
  titre: "Creneaux d amarrage",
  titreEn: "Berthing slots",
  description: "Attribution de postes d amarrage par creneau.",
  descriptionEn: "Berth allocation per time slot.",
  aide: "Evite conflit d occupation des appontements.",
  aideEn: "Avoids berth occupancy conflict.",
  lister: (params) => api.lister("flvb-berthing-slots", params),
  creer: (data) => api.creer("flvb-berthing-slots", data),
  modifier: (id, data) => api.modifier("flvb-berthing-slots", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference creneau", "Slot reference"),
    col("terminal", "Terminal", "Terminal"),
    col("numero_appontement", "Appontement", "Berth"),
    col("numero_flotte", "Bateau", "Vessel"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference creneau", "Slot reference", { requisCreation: true }),
    txt("terminal", "Terminal", "Terminal"),
    txt("numero_appontement", "Appontement", "Berth"),
    txt("numero_flotte", "Bateau", "Vessel"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialCrewRoster: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "crew_roster",
  tcode: "registre-crew-rosters-river",
  icon: Icons.Users,
  titre: "Equipages fluviaux",
  titreEn: "River crew rosters",
  description: "Affectation des equipes par bateau et par rotation.",
  descriptionEn: "Crew assignment per vessel and rotation.",
  aide: "Controle temps de repos reglementaire.",
  aideEn: "Regulatory rest-time check.",
  lister: (params) => api.lister("flvb-crew-rosters", params),
  creer: (data) => api.creer("flvb-crew-rosters", data),
  modifier: (id, data) => api.modifier("flvb-crew-rosters", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference rotation", "Rotation reference"),
    col("numero_flotte", "Bateau", "Vessel"),
    col("chef_bord", "Chef de bord", "Captain"),
    col("nb_marins", "Nb marins", "Crew size"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("heures_service", "Heures service", "Service hours"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference rotation", "Rotation reference", { requisCreation: true }),
    txt("numero_flotte", "Bateau", "Vessel"),
    txt("chef_bord", "Chef de bord", "Captain"),
    num("nb_marins", "Nb marins", "Crew size"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    num("heures_service", "Heures service", "Service hours"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialCargoManifest: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "cargo_manifest",
  tcode: "registre-cargo-manifests-river",
  icon: Icons.ListChecks,
  titre: "Manifestes de chargement fluviaux",
  titreEn: "River cargo manifests",
  description: "Liste des marchandises chargees par convoi.",
  descriptionEn: "Goods loaded per convoy.",
  aide: "Piece jointe a la lettre de voiture CMNI.",
  aideEn: "Annex to the CMNI waybill.",
  lister: (params) => api.lister("flvb-cargo-manifests", params),
  creer: (data) => api.creer("flvb-cargo-manifests", data),
  modifier: (id, data) => api.modifier("flvb-cargo-manifests", id, data),
  unicite: "numero_manifeste",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_manifeste", "Numero manifeste", "Manifest number"),
    col("numero_convoi", "Convoi", "Convoy"),
    col("terminal_depart", "Depart", "Origin terminal"),
    col("terminal_arrivee", "Arrivee", "Destination terminal"),
    col("nb_colis", "Nb colis", "Items"),
    col("masse_total_t", "Masse totale (t)", "Total mass (t)"),
    col("date_emission", "Date emission", "Issue date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_manifeste", "Numero manifeste", "Manifest number", { requisCreation: true }),
    txt("numero_convoi", "Convoi", "Convoy"),
    txt("terminal_depart", "Depart", "Origin terminal"),
    txt("terminal_arrivee", "Arrivee", "Destination terminal"),
    num("nb_colis", "Nb colis", "Items"),
    num("masse_total_t", "Masse totale (t)", "Total mass (t)"),
    dt("date_emission", "Date emission", "Issue date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialPortFee: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "port_fee",
  tcode: "registre-port-fees-river",
  icon: Icons.Receipt,
  titre: "Droits de port fluvial",
  titreEn: "River port dues",
  description: "Tarifs de stationnement et de manutention par terminal.",
  descriptionEn: "Berthing and handling dues per terminal.",
  aide: "Factures au bateau ou au chargeur.",
  aideEn: "Billed to vessel or shipper.",
  lister: (params) => api.lister("flvb-port-fees", params),
  creer: (data) => api.creer("flvb-port-fees", data),
  modifier: (id, data) => api.modifier("flvb-port-fees", id, data),
  unicite: "code_tarif",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tarif", "Code tarif", "Fee code"),
    col("terminal", "Terminal", "Terminal"),
    col("categorie", "Categorie", "Category"),
    col("assiette", "Assiette", "Basis"),
    col("montant_xaf", "Montant (XAF)", "Amount (XAF)"),
    col("unite", "Unite", "Unit"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_tarif", "Code tarif", "Fee code", { requisCreation: true }),
    txt("terminal", "Terminal", "Terminal"),
    txt("categorie", "Categorie", "Category"),
    txt("assiette", "Assiette", "Basis"),
    num("montant_xaf", "Montant (XAF)", "Amount (XAF)"),
    txt("unite", "Unite", "Unit"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialVesselInspection: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "vessel_inspection",
  tcode: "registre-vessel-inspections",
  icon: Icons.ClipboardCheck,
  titre: "Visites techniques batellerie",
  titreEn: "Vessel technical inspections",
  description: "Controles reglementaires des bateaux (communautaire/national).",
  descriptionEn: "Regulatory vessel checks (EU/national).",
  aide: "Conditionne la mise en service.",
  aideEn: "Gates vessel release to service.",
  lister: (params) => api.lister("flvb-vessel-inspections", params),
  creer: (data) => api.creer("flvb-vessel-inspections", data),
  modifier: (id, data) => api.modifier("flvb-vessel-inspections", id, data),
  unicite: "numero_pv",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_pv", "Numero PV", "Report number"),
    col("numero_flotte", "Bateau", "Vessel"),
    col("type_visite", "Type visite", "Inspection type"),
    col("date_visite", "Date visite", "Inspection date"),
    col("date_echeance", "Echeance", "Due date"),
    col("resultat", "Resultat", "Result"),
    col("observations", "Observations", "Observations"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_pv", "Numero PV", "Report number", { requisCreation: true }),
    txt("numero_flotte", "Bateau", "Vessel"),
    txt("type_visite", "Type visite", "Inspection type"),
    dt("date_visite", "Date visite", "Inspection date"),
    dt("date_echeance", "Echeance", "Due date"),
    txt("resultat", "Resultat", "Result"),
    txt("observations", "Observations", "Observations"),
    txt("statut", "Statut", "Status"),
  ],
};

