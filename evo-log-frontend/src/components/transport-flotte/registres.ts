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

export const registreVehicleRegistration: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "vehicle_registry",
  tcode: "registre-vehicle-registry",
  icon: Icons.Truck,
  titre: "Fiche vehicule",
  titreEn: "Vehicle record",
  description: "Registre technique des vehicules de la flotte.",
  descriptionEn: "Technical registry of fleet vehicles.",
  aide: "Chaque vehicule doit disposer d'une carte grise valide.",
  aideEn: "Each vehicle must have a valid registration.",
  lister: (params) => api.lister("vehicle-registrations", params),
  creer: (data) => api.creer("vehicle-registrations", data),
  modifier: (id, data) => api.modifier("vehicle-registrations", id, data),
  unicite: "numero_immatriculation",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_immatriculation", "Immatriculation", "Plate"),
    col("marque", "Marque", "Brand"),
    col("modele", "Modele", "Model"),
    col("annee_mise_circulation", "Annee", "Year"),
    col("type_vehicule", "Type", "Type"),
    col("ptt_tonnes", "PTT (t)", "GVW (t)"),
    col("puissance_cv", "Puissance (CV)", "Power (CV)"),
    col("kilometrage_actuel", "Kilometrage", "Odometer"),
    col("couleur", "Couleur", "Color"),
    col("carrosserie", "Carrosserie", "Body"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_immatriculation", "Immatriculation", "Plate", { requisCreation: true }),
    txt("marque", "Marque", "Brand"),
    txt("modele", "Modele", "Model"),
    num("annee_mise_circulation", "Annee", "Year"),
    sel("type_vehicule", "Type", "Type", "type_vehicule"),
    num("ptt_tonnes", "PTT (t)", "GVW (t)"),
    num("puissance_cv", "Puissance (CV)", "Power (CV)"),
    num("kilometrage_actuel", "Kilometrage", "Odometer"),
    txt("couleur", "Couleur", "Color"),
    txt("carrosserie", "Carrosserie", "Body"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreRoutePlan: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "route_plan",
  tcode: "registre-route-planning",
  icon: Icons.Route,
  titre: "Planification tournees",
  titreEn: "Route planning",
  description: "Tournees de livraison et collecte optimisees.",
  descriptionEn: "Optimized delivery/pickup routes.",
  aide: "L'optimisation VRP doit rester sous le seuil de service.",
  aideEn: "VRP optimization must remain under service threshold.",
  lister: (params) => api.lister("route-plans", params),
  creer: (data) => api.creer("route-plans", data),
  modifier: (id, data) => api.modifier("route-plans", id, data),
  unicite: "code_tournee",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tournee", "Code tournee", "Route code"),
    col("date_tournee", "Date", "Date"),
    col("chauffeur_id", "Chauffeur", "Driver"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("nb_points", "Nb points", "Stops"),
    col("distance_km", "Distance (km)", "Distance (km)"),
    col("duree_estimee_h", "Duree estimee", "Est. duration"),
    col("zonale", "Zone", "Zone"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("code_tournee", "Code tournee", "Route code", { requisCreation: true }),
    dt("date_tournee", "Date", "Date"),
    num("chauffeur_id", "Chauffeur", "Driver"),
    num("vehicule_id", "Vehicule", "Vehicle"),
    num("nb_points", "Nb points", "Stops"),
    num("distance_km", "Distance (km)", "Distance (km)"),
    num("duree_estimee_h", "Duree estimee", "Est. duration"),
    txt("zonale", "Zone", "Zone"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreCheckpointControl: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "checkpoint",
  tcode: "registre-checkpoint-tracking",
  icon: Icons.MapPin,
  titre: "Controles routiers et pesages",
  titreEn: "Roadside checks and weigh-ins",
  description: "Controles effectues aux balises et ponts-bascules.",
  descriptionEn: "Checks performed at checkpoints and weighbridges.",
  aide: "Un depot de poids declare un litige imminent.",
  aideEn: "Overweight declaration signals imminent dispute.",
  lister: (params) => api.lister("checkpoint-controls", params),
  creer: (data) => api.creer("checkpoint-controls", data),
  modifier: (id, data) => api.modifier("checkpoint-controls", id, data),
  unicite: "numero_pv",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_pv", "Numero PV", "Report number"),
    col("date_controle", "Date", "Date"),
    col("lieu", "Lieu", "Location"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("poids_reel_t", "Poids reel (t)", "Actual weight (t)"),
    col("poids_autorise_t", "Poids autorise (t)", "Allowed weight (t)"),
    col("type_controle", "Type", "Type"),
    col("agent", "Agent", "Agent"),
    col("sanction_appliquee", "Sanction", "Sanction"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_pv", "Numero PV", "Report number", { requisCreation: true }),
    dtx("date_controle", "Date", "Date"),
    txt("lieu", "Lieu", "Location"),
    num("vehicule_id", "Vehicule", "Vehicle"),
    num("poids_reel_t", "Poids reel (t)", "Actual weight (t)"),
    num("poids_autorise_t", "Poids autorise (t)", "Allowed weight (t)"),
    sel("type_controle", "Type", "Type", "type_controle"),
    txt("agent", "Agent", "Agent"),
    txt("sanction_appliquee", "Sanction", "Sanction"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreCargoInsurance: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "cargo_insurance",
  tcode: "registre-cargo-insurance",
  icon: Icons.Shield,
  titre: "Assurance marchandise transportee",
  titreEn: "Cargo insurance",
  description: "Polices d'assurance fret par type de transport.",
  descriptionEn: "Freight insurance policies per transport type.",
  aide: "Une franchise mal parametree expose l'exploitant.",
  aideEn: "Poorly set deductible exposes the operator.",
  lister: (params) => api.lister("cargo-insurances", params),
  creer: (data) => api.creer("cargo-insurances", data),
  modifier: (id, data) => api.modifier("cargo-insurances", id, data),
  unicite: "numero_police",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_police", "Numero police", "Policy number"),
    col("assureur", "Assureur", "Insurer"),
    col("type_garantie", "Type garantie", "Coverage"),
    col("plafond_xaf", "Plafond XAF", "Coverage cap XAF"),
    col("franchise_xaf", "Franchise XAF", "Deductible XAF"),
    col("prime_xaf", "Prime XAF", "Premium XAF"),
    col("date_effet", "Date effet", "Inception"),
    col("date_fin", "Date fin", "Expiry"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_police", "Numero police", "Policy number", { requisCreation: true }),
    txt("assureur", "Assureur", "Insurer"),
    sel("type_garantie", "Type garantie", "Coverage", "type_garantie"),
    num("plafond_xaf", "Plafond XAF", "Coverage cap XAF"),
    num("franchise_xaf", "Franchise XAF", "Deductible XAF"),
    num("prime_xaf", "Prime XAF", "Premium XAF"),
    dt("date_effet", "Date effet", "Inception"),
    dt("date_fin", "Date fin", "Expiry"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreFreightBill: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "freight_billing",
  tcode: "registre-freight-billing",
  icon: Icons.Receipt,
  titre: "Facturation fret",
  titreEn: "Freight billing",
  description: "Factures de transport, accessoires et supplement.",
  descriptionEn: "Transport invoices, extras and surcharges.",
  aide: "Facture client = support de la revue de creance.",
  aideEn: "Customer invoice = basis of receivable review.",
  lister: (params) => api.lister("freight-bills", params),
  creer: (data) => api.creer("freight-bills", data),
  modifier: (id, data) => api.modifier("freight-bills", id, data),
  unicite: "numero_facture",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_facture", "Numero", "Number"),
    col("client_id", "Client", "Client"),
    col("mission_id", "Mission", "Mission"),
    col("montant_ht_xaf", "Montant HT", "Amount excl. tax"),
    col("tva_xaf", "TVA", "VAT"),
    col("total_ttc_xaf", "Total TTC", "Total incl. tax"),
    col("date_emission", "Date emission", "Issue date"),
    col("date_echeance", "Echeance", "Due date"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_facture", "Numero", "Number", { requisCreation: true }),
    num("client_id", "Client", "Client"),
    num("mission_id", "Mission", "Mission"),
    num("montant_ht_xaf", "Montant HT", "Amount excl. tax"),
    num("tva_xaf", "TVA", "VAT"),
    num("total_ttc_xaf", "Total TTC", "Total incl. tax"),
    dt("date_emission", "Date emission", "Issue date"),
    dt("date_echeance", "Echeance", "Due date"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreSubcontractor: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "subcontractor",
  tcode: "registre-subcontractors",
  icon: Icons.Users,
  titre: "Transporteurs sous-traitants",
  titreEn: "Subcontracted carriers",
  description: "Referentiel des transporteurs externes et capacites.",
  descriptionEn: "External carriers and capabilities register.",
  aide: "Verifier agrement et assurance avant affectation.",
  aideEn: "Verify approval and insurance before assignment.",
  lister: (params) => api.lister("subcontractors", params),
  creer: (data) => api.creer("subcontractors", data),
  modifier: (id, data) => api.modifier("subcontractors", id, data),
  unicite: "code_sous_traitant",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_sous_traitant", "Code", "Code"),
    col("raison_sociale", "Raison sociale", "Legal name"),
    col("niu", "NIU", "Tax ID"),
    col("contact", "Contact", "Contact"),
    col("telephone", "Telephone", "Phone"),
    col("nb_camions", "Nb camions", "Trucks"),
    col("zones_couvertes", "Zones couvertes", "Zones covered"),
    col("agreement_numero", "Numero agrement", "Approval number"),
    col("date_expiration_agreement", "Expiration agrement", "Approval expiry"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_sous_traitant", "Code", "Code", { requisCreation: true }),
    txt("raison_sociale", "Raison sociale", "Legal name"),
    txt("niu", "NIU", "Tax ID"),
    txt("contact", "Contact", "Contact"),
    txt("telephone", "Telephone", "Phone"),
    num("nb_camions", "Nb camions", "Trucks"),
    txt("zones_couvertes", "Zones couvertes", "Zones covered"),
    txt("agreement_numero", "Numero agrement", "Approval number"),
    dt("date_expiration_agreement", "Expiration agrement", "Approval expiry"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreDangerousGoodsLoad: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "dangerous_goods",
  tcode: "registre-dangerous-goods",
  icon: Icons.AlertTriangle,
  titre: "Marchandises dangereuses ADR",
  titreEn: "ADR dangerous goods",
  description: "Cargaisons classees ADR avec numero ONU.",
  descriptionEn: "ADR-classified loads with UN number.",
  aide: "Etiquetage et document de transport obligatoires.",
  aideEn: "Placarding and transport document mandatory.",
  lister: (params) => api.lister("dangerous-goods-loads", params),
  creer: (data) => api.creer("dangerous-goods-loads", data),
  modifier: (id, data) => api.modifier("dangerous-goods-loads", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("mission_id", "Mission", "Mission"),
    col("onu_number", "Numero ONU", "UN number"),
    col("classe_adr", "Classe ADR", "ADR class"),
    col("designation_officielle", "Designation", "Official name"),
    col("groupe_emballage", "Groupe emballage", "Packing group"),
    col("quantite_kg", "Quantite (kg)", "Quantity (kg)"),
    col("etiquettes", "Etiquettes", "Labels"),
    col("formation_chauffeur", "Formation chauffeur ADR", "Driver ADR training"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("mission_id", "Mission", "Mission"),
    txt("onu_number", "Numero ONU", "UN number"),
    txt("classe_adr", "Classe ADR", "ADR class"),
    txt("designation_officielle", "Designation", "Official name"),
    sel("groupe_emballage", "Groupe emballage", "Packing group", "groupe_emballage"),
    num("quantite_kg", "Quantite (kg)", "Quantity (kg)"),
    txt("etiquettes", "Etiquettes", "Labels"),
    chk("formation_chauffeur", "Formation chauffeur ADR", "Driver ADR training"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreVehicleDocument: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "vehicle_document",
  tcode: "registre-vehicle-documents",
  icon: Icons.FileText,
  titre: "Cartes grises / assurances / vignettes",
  titreEn: "Registration / insurance / stickers",
  description: "Documents obligatoires par vehicule.",
  descriptionEn: "Mandatory documents per vehicle.",
  aide: "Tout document expire immobilise le vehicule.",
  aideEn: "Any expired document immobilizes the vehicle.",
  lister: (params) => api.lister("vehicle-documents", params),
  creer: (data) => api.creer("vehicle-documents", data),
  modifier: (id, data) => api.modifier("vehicle-documents", id, data),
  unicite: "numero_document",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_document", "Numero document", "Document number"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("type_document", "Type", "Type"),
    col("autorite_emission", "Autorite emission", "Issuing authority"),
    col("date_emission", "Date emission", "Issue date"),
    col("date_expiration", "Date expiration", "Expiry date"),
    col("numero_police_associe", "Numero police", "Policy number"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_document", "Numero document", "Document number", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    sel("type_document", "Type", "Type", "type_document"),
    txt("autorite_emission", "Autorite emission", "Issuing authority"),
    dt("date_emission", "Date emission", "Issue date"),
    dt("date_expiration", "Date expiration", "Expiry date"),
    txt("numero_police_associe", "Numero police", "Policy number"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreGpsDevice: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "gps_device",
  tcode: "registre-gps-devices",
  icon: Icons.Satellite,
  titre: "Boitiers GPS / telematique",
  titreEn: "GPS / telematics devices",
  description: "Inventaire boitiers et plans de suivi.",
  descriptionEn: "Device inventory and tracking plans.",
  aide: "Un boitier hors reseau doit etre remplace sous 48h.",
  aideEn: "Offline device must be replaced within 48h.",
  lister: (params) => api.lister("gps-devices", params),
  creer: (data) => api.creer("gps-devices", data),
  modifier: (id, data) => api.modifier("gps-devices", id, data),
  unicite: "numero_serial_gps",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_serial_gps", "Numero serie", "Serial number"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("fournisseur", "Fournisseur", "Provider"),
    col("modele", "Modele", "Model"),
    col("numero_sim", "Numero SIM", "SIM number"),
    col("date_installation", "Installation", "Installation date"),
    col("date_derniere_communication", "Derniere comm.", "Last communication"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_serial_gps", "Numero serie", "Serial number", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    txt("fournisseur", "Fournisseur", "Provider"),
    txt("modele", "Modele", "Model"),
    txt("numero_sim", "Numero SIM", "SIM number"),
    dt("date_installation", "Installation", "Installation date"),
    dtx("date_derniere_communication", "Derniere comm.", "Last communication"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreTrafficPenalty: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "penalty",
  tcode: "registre-penalty-tracking",
  icon: Icons.Ticket,
  titre: "Infractions et PV routiers",
  titreEn: "Traffic violations and fines",
  description: "PV recus, suites donnees, reglement.",
  descriptionEn: "Received fines, actions and payments.",
  aide: "Contester dans le delai legal (30j).",
  aideEn: "Dispute within the legal window (30 days).",
  lister: (params) => api.lister("traffic-penalties", params),
  creer: (data) => api.creer("traffic-penalties", data),
  modifier: (id, data) => api.modifier("traffic-penalties", id, data),
  unicite: "numero_pv",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_pv", "Numero PV", "Report number"),
    col("vehicule_id", "Vehicule", "Vehicle"),
    col("date_infraction", "Date infraction", "Offense date"),
    col("lieu", "Lieu", "Location"),
    col("type_infraction", "Type", "Type"),
    col("montant_amende_xaf", "Amende XAF", "Fine XAF"),
    col("points_retires", "Points retires", "Points removed"),
    col("chauffeur_id", "Chauffeur", "Driver"),
    col("statut", "Statut", "Status"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("numero_pv", "Numero PV", "Report number", { requisCreation: true }),
    num("vehicule_id", "Vehicule", "Vehicle"),
    dt("date_infraction", "Date infraction", "Offense date"),
    txt("lieu", "Lieu", "Location"),
    sel("type_infraction", "Type", "Type", "type_infraction"),
    num("montant_amende_xaf", "Amende XAF", "Fine XAF"),
    num("points_retires", "Points retires", "Points removed"),
    num("chauffeur_id", "Chauffeur", "Driver"),
    sel("statut", "Statut", "Status", "statut"),
    txt("notes", "Notes", "Notes"),
  ],
};


export const registreConvoy: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "convoy",
  tcode: "registre-convoy-management",
  icon: Icons.Users,
  titre: "Convois et escorte",
  titreEn: "Convoys and escort",
  description: "Groupements de vehicules sous escorte armee ou civile.",
  descriptionEn: "Vehicle groups under armed or civilian escort.",
  aide: "Le chef de convoi valide le depart et l'arrivee.",
  aideEn: "Convoy lead authorizes departure and arrival.",
  lister: (params) => api.lister("convoys", params),
  creer: (data) => api.creer("convoys", data),
  modifier: (id, data) => api.modifier("convoys", id, data),
  unicite: "code_convoi",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_convoi", "Code convoi", "Convoy code"),
    col("date_depart", "Depart", "Departure"),
    col("date_arrivee", "Arrivee", "Arrival"),
    col("nb_vehicules", "Nb vehicules", "Vehicles"),
    col("type_escorte", "Type escorte", "Escort type"),
    col("chef_convoi", "Chef de convoi", "Convoy lead"),
    col("itineraire", "Itineraire", "Route"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_convoi", "Code convoi", "Convoy code", { requisCreation: true }),
    dtx("date_depart", "Depart", "Departure"),
    dtx("date_arrivee", "Arrivee", "Arrival"),
    num("nb_vehicules", "Nb vehicules", "Vehicles"),
    sel("type_escorte", "Type escorte", "Escort type", "type_escorte"),
    txt("chef_convoi", "Chef de convoi", "Convoy lead"),
    txt("itineraire", "Itineraire", "Route"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreFleetKpi: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "performance_kpi",
  tcode: "registre-performance-kpi",
  icon: Icons.TrendingUp,
  titre: "TCO et taux de service",
  titreEn: "TCO and service rate",
  description: "Indicateurs de performance de la flotte.",
  descriptionEn: "Fleet performance indicators.",
  aide: "TCO calcule mensuellement par tranche.",
  aideEn: "TCO calculated monthly by segment.",
  lister: (params) => api.lister("fleet-kpis", params),
  creer: (data) => api.creer("fleet-kpis", data),
  modifier: (id, data) => api.modifier("fleet-kpis", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("periode_debut", "Debut periode", "Period start"),
    col("periode_fin", "Fin periode", "Period end"),
    col("cout_total_xaf", "Cout total", "Total cost"),
    col("km_parcourus", "Km parcourus", "Kilometers"),
    col("cout_par_km", "Cout par km", "Cost per km"),
    col("taux_dispo_pct", "Taux dispo %", "Availability %"),
    col("taux_service_pct", "Taux service %", "Service rate %"),
    col("nb_accidents", "Accidents", "Accidents"),
    col("notes", "Notes", "Notes"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    dt("periode_debut", "Debut periode", "Period start"),
    dt("periode_fin", "Fin periode", "Period end"),
    num("cout_total_xaf", "Cout total", "Total cost"),
    num("km_parcourus", "Km parcourus", "Kilometers"),
    num("cout_par_km", "Cout par km", "Cost per km"),
    num("taux_dispo_pct", "Taux dispo %", "Availability %"),
    num("taux_service_pct", "Taux service %", "Service rate %"),
    num("nb_accidents", "Accidents", "Accidents"),
    txt("notes", "Notes", "Notes"),
  ],
};

