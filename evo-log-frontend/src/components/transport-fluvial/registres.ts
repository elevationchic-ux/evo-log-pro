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

export const registreFluvialBarge: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "barge_fleet",
  tcode: "registre-barge-fleet",
  icon: Icons.Ship,
  titre: "Flotte peniches / chalands",
  titreEn: "Barge fleet",
  description: "Referentiel peniches, chalands et automoteurs fluviaux.",
  descriptionEn: "Barges, lighters and self-propelled craft.",
  aide: "Tirant d'eau max selon saison / voie.",
  aideEn: "Max draft per season/channel.",
  lister: (params) => api.lister("fluvial-barges", params),
  creer: (data) => api.creer("fluvial-barges", data),
  modifier: (id, data) => api.modifier("fluvial-barges", id, data),
  unicite: "numero_flotte",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_flotte", "Numero flotte", "Fleet number"),
    col("type", "Type", "Type"),
    col("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    col("tirant_eau_max_m", "Tirant d'eau max (m)", "Max draft (m)"),
    col("longueur_m", "Longueur (m)", "Length (m)"),
    col("largeur_m", "Largeur (m)", "Beam (m)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_flotte", "Numero flotte", "Fleet number", { requisCreation: true }),
    txt("type", "Type", "Type"),
    num("capacite_tonnes", "Capacite (t)", "Capacity (t)"),
    txt("tirant_eau_max_m", "Tirant d'eau max (m)", "Max draft (m)"),
    num("longueur_m", "Longueur (m)", "Length (m)"),
    num("largeur_m", "Largeur (m)", "Beam (m)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialTowboat: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "tow_fleet",
  tcode: "registre-tow-fleet",
  icon: Icons.Anchor,
  titre: "Remorqueurs fluviaux",
  titreEn: "River tug fleet",
  description: "Remorqueurs d'estuaire et de voie interieure.",
  descriptionEn: "Estuary and inland waterway tugs.",
  aide: "Puissance bollee pour convois.",
  aideEn: "Bollard pull rated for convoys.",
  lister: (params) => api.lister("fluvial-towboats", params),
  creer: (data) => api.creer("fluvial-towboats", data),
  modifier: (id, data) => api.modifier("fluvial-towboats", id, data),
  unicite: "numero_tug",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_tug", "Numero remorqueur", "Tug number"),
    col("nom", "Nom", "Name"),
    col("puissance_kw", "Puissance (kW)", "Power (kW)"),
    col("bollard_pull_t", "Bollard pull (t)", "Bollard pull (t)"),
    col("zone_operation", "Zone operation", "Operating area"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_tug", "Numero remorqueur", "Tug number", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    num("puissance_kw", "Puissance (kW)", "Power (kW)"),
    num("bollard_pull_t", "Bollard pull (t)", "Bollard pull (t)"),
    txt("zone_operation", "Zone operation", "Operating area"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreLockTransit: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "locks",
  tcode: "registre-lock-transits",
  icon: Icons.DoorOpen,
  titre: "Transits d'ecluses",
  titreEn: "Lock transits",
  description: "Passages d'ecluses avec horaires, poids, dimensions.",
  descriptionEn: "Lock passages with timing, weight, dimensions.",
  aide: "Reservation obligatoire via VNF/COPR.",
  aideEn: "Mandatory reservation.",
  lister: (params) => api.lister("fluvial-lock-transits", params),
  creer: (data) => api.creer("fluvial-lock-transits", data),
  modifier: (id, data) => api.modifier("fluvial-lock-transits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference passage", "Transit reference"),
    col("nom_ecluse", "Nom ecluse", "Lock name"),
    col("date_passage", "Date passage", "Transit date"),
    col("numero_peniche", "Peniche concernee", "Barge number"),
    col("masse_tonnes", "Masse (t)", "Mass (t)"),
    col("tirant_eau_m", "Tirant d'eau (m)", "Draft (m)"),
    col("attente_minutes", "Attente (min)", "Waiting (min)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference passage", "Transit reference", { requisCreation: true }),
    txt("nom_ecluse", "Nom ecluse", "Lock name"),
    dtx("date_passage", "Date passage", "Transit date"),
    txt("numero_peniche", "Peniche concernee", "Barge number"),
    num("masse_tonnes", "Masse (t)", "Mass (t)"),
    txt("tirant_eau_m", "Tirant d'eau (m)", "Draft (m)"),
    num("attente_minutes", "Attente (min)", "Waiting (min)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreRiverDepthSurvey: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "depth",
  tcode: "registre-river-depth",
  icon: Icons.Ruler,
  titre: "Sondes bathymetriques",
  titreEn: "River depth surveys",
  description: "Mesures periodiques de fond de voie / seuils / tirant d'eau pratique.",
  descriptionEn: "Periodic bed / threshold / practical draft survey.",
  aide: "Declenche restriction de tirant d'eau.",
  aideEn: "Triggers draft restriction.",
  lister: (params) => api.lister("fluvial-depth-surveys", params),
  creer: (data) => api.creer("fluvial-depth-surveys", data),
  modifier: (id, data) => api.modifier("fluvial-depth-surveys", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("bief", "Bief", "Reach"),
    col("date_mesure", "Date mesure", "Survey date"),
    col("profondeur_min_cm", "Profondeur min (cm)", "Min depth (cm)"),
    col("tirant_eau_pmax_cm", "TPE pratique max (cm)", "Max practical draft (cm)"),
    col("debit_m3s", "Debit (m3/s)", "Flow (m3/s)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("bief", "Bief", "Reach"),
    dt("date_mesure", "Date mesure", "Survey date"),
    num("profondeur_min_cm", "Profondeur min (cm)", "Min depth (cm)"),
    num("tirant_eau_pmax_cm", "TPE pratique max (cm)", "Max practical draft (cm)"),
    num("debit_m3s", "Debit (m3/s)", "Flow (m3/s)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialTerminal: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "terminals",
  tcode: "registre-river-ports",
  icon: Icons.Warehouse,
  titre: "Terminaux fluviaux",
  titreEn: "River terminals",
  description: "Quais, appontements et zones de transbordement fluvial.",
  descriptionEn: "Quays, jetties and transshipment areas.",
  aide: "Connecte au port maritime (hinterland).",
  aideEn: "Linked to seaport (hinterland).",
  lister: (params) => api.lister("fluvial-terminals", params),
  creer: (data) => api.creer("fluvial-terminals", data),
  modifier: (id, data) => api.modifier("fluvial-terminals", id, data),
  unicite: "code_terminal",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_terminal", "Code terminal", "Terminal code"),
    col("nom", "Nom", "Name"),
    col("fleuve", "Fleuve", "River"),
    col("pays", "Pays", "Country"),
    col("nb_appontements", "Nb appontements", "Berths"),
    col("longueur_quai_m", "Longueur quai (m)", "Quay length (m)"),
    col("connecte_port_maritime", "Relie port maritime", "Connected to seaport"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_terminal", "Code terminal", "Terminal code", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("fleuve", "Fleuve", "River"),
    txt("pays", "Pays", "Country"),
    num("nb_appontements", "Nb appontements", "Berths"),
    num("longueur_quai_m", "Longueur quai (m)", "Quay length (m)"),
    chk("connecte_port_maritime", "Relie port maritime", "Connected to seaport"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialBulkOperation: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "bulk",
  tcode: "registre-bulk-river",
  icon: Icons.Droplet,
  titre: "Vrac fluvial",
  titreEn: "River bulk operations",
  description: "Chargement/dechargement vrac solide ou liquide.",
  descriptionEn: "Bulk solid or liquid loading/unloading.",
  aide: "Pompage / grue / banderoule selon produit.",
  aideEn: "Pump / crane / belt per product.",
  lister: (params) => api.lister("fluvial-bulk-operations", params),
  creer: (data) => api.creer("fluvial-bulk-operations", data),
  modifier: (id, data) => api.modifier("fluvial-bulk-operations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference operation", "Operation reference"),
    col("produit", "Produit", "Product"),
    col("categorie", "Categorie", "Category"),
    col("quantite_tonnes", "Quantite (t)", "Quantity (t)"),
    col("terminal", "Terminal", "Terminal"),
    col("date_operation", "Date", "Date"),
    col("duree_heures", "Duree (h)", "Duration (h)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference operation", "Operation reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    txt("categorie", "Categorie", "Category"),
    num("quantite_tonnes", "Quantite (t)", "Quantity (t)"),
    txt("terminal", "Terminal", "Terminal"),
    dtx("date_operation", "Date", "Date"),
    num("duree_heures", "Duree (h)", "Duration (h)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialSafetyRecord: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "safety",
  tcode: "registre-navigation-safety",
  icon: Icons.LifeBuoy,
  titre: "Securite navigation",
  titreEn: "Navigation safety",
  description: "Balises, accidents, secours, arret technique.",
  descriptionEn: "Beacons, incidents, rescue, technical stops.",
  aide: "Declenchement plan ORSEC si accident grave.",
  aideEn: "ORSEC plan trigger for serious incidents.",
  lister: (params) => api.lister("fluvial-safety-records", params),
  creer: (data) => api.creer("fluvial-safety-records", data),
  modifier: (id, data) => api.modifier("fluvial-safety-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("date_evenement", "Date evenement", "Event date"),
    col("bief", "Bief", "Reach"),
    col("type_evenement", "Type evenement", "Event type"),
    col("gravite", "Gravite", "Severity"),
    col("batiments_impliques", "Batiments impliques", "Vessels involved"),
    col("description", "Description", "Description"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    dtx("date_evenement", "Date evenement", "Event date"),
    txt("bief", "Bief", "Reach"),
    txt("type_evenement", "Type evenement", "Event type"),
    txt("gravite", "Gravite", "Severity"),
    txt("batiments_impliques", "Batiments impliques", "Vessels involved"),
    txt("description", "Description", "Description"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialTariff: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "tariffs",
  tcode: "registre-river-tariffs",
  icon: Icons.Calculator,
  titre: "Tarification fluviale",
  titreEn: "River tariffs",
  description: "Prix par tonne / km selon bief et type produit.",
  descriptionEn: "Price per ton-km per reach and product.",
  aide: "Refacte selon niveau d'eau / saison.",
  aideEn: "Adjusted per water level / season.",
  lister: (params) => api.lister("fluvial-tariffs", params),
  creer: (data) => api.creer("fluvial-tariffs", data),
  modifier: (id, data) => api.modifier("fluvial-tariffs", id, data),
  unicite: "code_tarif",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tarif", "Code tarif", "Tariff code"),
    col("bief", "Bief", "Reach"),
    col("produit", "Produit", "Product"),
    col("prix_par_tonne_xaf", "Prix (XAF/t)", "Price (XAF/t)"),
    col("saisonnalite", "Saisonnalite", "Season"),
    col("remise_volume_pct", "Remise volume (%)", "Volume discount (%)"),
    col("validite_debut", "Debut validite", "Valid from"),
    col("validite_fin", "Fin validite", "Valid until"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_tarif", "Code tarif", "Tariff code", { requisCreation: true }),
    txt("bief", "Bief", "Reach"),
    txt("produit", "Produit", "Product"),
    num("prix_par_tonne_xaf", "Prix (XAF/t)", "Price (XAF/t)"),
    txt("saisonnalite", "Saisonnalite", "Season"),
    num("remise_volume_pct", "Remise volume (%)", "Volume discount (%)"),
    dt("validite_debut", "Debut validite", "Valid from"),
    dt("validite_fin", "Fin validite", "Valid until"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialWaybill: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "waybills",
  tcode: "registre-river-waybills",
  icon: Icons.FileText,
  titre: "Lettres de voiture fluviale CMNI",
  titreEn: "CMNI inland waybills",
  description: "Titres de transport CMNI / nationaux fluviaux.",
  descriptionEn: "CMNI or national inland waybills.",
  aide: "Applicable sur Rhin, Senegal, Congo.",
  aideEn: "Applies to Rhine, Senegal, Congo.",
  lister: (params) => api.lister("fluvial-waybills", params),
  creer: (data) => api.creer("fluvial-waybills", data),
  modifier: (id, data) => api.modifier("fluvial-waybills", id, data),
  unicite: "numero",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero", "Numero LCV fluviale", "Inland waybill number"),
    col("expediteur", "Expediteur", "Sender"),
    col("destinataire", "Destinataire", "Consignee"),
    col("port_depart", "Port depart", "Loading port"),
    col("port_arrivee", "Port arrivee", "Discharge port"),
    col("produit", "Produit", "Product"),
    col("quantite_tonnes", "Quantite (t)", "Quantity (t)"),
    col("date_emission", "Date emission", "Issue date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero", "Numero LCV fluviale", "Inland waybill number", { requisCreation: true }),
    txt("expediteur", "Expediteur", "Sender"),
    txt("destinataire", "Destinataire", "Consignee"),
    txt("port_depart", "Port depart", "Loading port"),
    txt("port_arrivee", "Port arrivee", "Discharge port"),
    txt("produit", "Produit", "Product"),
    num("quantite_tonnes", "Quantite (t)", "Quantity (t)"),
    dt("date_emission", "Date emission", "Issue date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFluvialPosition: ConfigRegistre = {
  permModule: "fluvial",
  permSousModule: "positions",
  tcode: "registre-fleet-positioning",
  icon: Icons.MapPinned,
  titre: "Positionnement flotte fluviale",
  titreEn: "Fleet positioning",
  description: "AIS fluvial / GPS / VHF positionnement temps reel.",
  descriptionEn: "Inland AIS / GPS / VHF real-time positioning.",
  aide: "Declenche alerte si arret non prevu.",
  aideEn: "Alerts on unplanned stop.",
  lister: (params) => api.lister("fluvial-positions", params),
  creer: (data) => api.creer("fluvial-positions", data),
  modifier: (id, data) => api.modifier("fluvial-positions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference relevé", "Position reference"),
    col("numero_flotte", "Bateau", "Vessel"),
    col("date_releve", "Date releve", "Position date"),
    col("latitude", "Latitude", "Latitude"),
    col("longitude", "Longitude", "Longitude"),
    col("vitesse_nd", "Vitesse (nd)", "Speed (kn)"),
    col("cap", "Cap", "Heading"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference relevé", "Position reference", { requisCreation: true }),
    txt("numero_flotte", "Bateau", "Vessel"),
    dtx("date_releve", "Date releve", "Position date"),
    txt("latitude", "Latitude", "Latitude"),
    txt("longitude", "Longitude", "Longitude"),
    txt("vitesse_nd", "Vitesse (nd)", "Speed (kn)"),
    txt("cap", "Cap", "Heading"),
    txt("statut", "Statut", "Status"),
  ],
};

