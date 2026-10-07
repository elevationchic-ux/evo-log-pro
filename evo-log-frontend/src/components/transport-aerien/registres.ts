/**
 * Configs Registre pour transport-aerien (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("transport-aerien");

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

export const registreAircraft: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "fleet",
  tcode: "registre-aircraft-fleet",
  icon: Icons.Plane,
  titre: "Flotte aeronefs",
  titreEn: "Aircraft fleet",
  description: "Avions cargo, passagers et mixtes.",
  descriptionEn: "Cargo, passenger and combi aircraft.",
  aide: "Navigabilite = certificat + checks a jour.",
  aideEn: "Airworthiness = certificate + up-to-date checks.",
  lister: (params) => api.lister("air-aircraft", params),
  creer: (data) => api.creer("air-aircraft", data),
  modifier: (id, data) => api.modifier("air-aircraft", id, data),
  unicite: "immatriculation",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("immatriculation", "Immatriculation", "Registration"),
    col("modele", "Modele", "Model"),
    col("operateur", "Operateur", "Operator"),
    col("capacite_tonnes", "Capacite (t)", "Payload (t)"),
    col("autonomie_km", "Autonomie (km)", "Range (km)"),
    col("heures_vol_total", "Heures vol totales", "Total flight hours"),
    col("certificat_navigabilite_fin", "Fin CofA", "CofA expiry"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("immatriculation", "Immatriculation", "Registration", { requisCreation: true }),
    txt("modele", "Modele", "Model"),
    txt("operateur", "Operateur", "Operator"),
    num("capacite_tonnes", "Capacite (t)", "Payload (t)"),
    num("autonomie_km", "Autonomie (km)", "Range (km)"),
    num("heures_vol_total", "Heures vol totales", "Total flight hours"),
    dt("certificat_navigabilite_fin", "Fin CofA", "CofA expiry"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAirWaybill: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "awb",
  tcode: "registre-air-waybills",
  icon: Icons.FileSignature,
  titre: "Lia / lettres de transport aerien",
  titreEn: "Air waybills",
  description: "AWB maitre (MAWB) et secondaire (HAWB).",
  descriptionEn: "Master (MAWB) and house (HAWB) air waybills.",
  aide: "Format IATA 3 chiffres + 8 chiffres + check digit.",
  aideEn: "IATA 3-8-1 digit format.",
  lister: (params) => api.lister("air-waybills", params),
  creer: (data) => api.creer("air-waybills", data),
  modifier: (id, data) => api.modifier("air-waybills", id, data),
  unicite: "numero_awb",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_awb", "Numero AWB", "AWB number"),
    col("type_awb", "Type AWB", "AWB type"),
    col("expediteur", "Expediteur", "Shipper"),
    col("destinataire", "Destinataire", "Consignee"),
    col("aeroport_depart", "Aeroport depart", "Departure airport"),
    col("aeroport_arrivee", "Aeroport arrivee", "Arrival airport"),
    col("nb_pieces", "Nombre de colis", "Pieces"),
    col("poids_kg", "Poids (kg)", "Weight (kg)"),
    col("valeur_declaree_xaf", "Valeur declaree", "Declared value"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_awb", "Numero AWB", "AWB number", { requisCreation: true }),
    txt("type_awb", "Type AWB", "AWB type"),
    txt("expediteur", "Expediteur", "Shipper"),
    txt("destinataire", "Destinataire", "Consignee"),
    txt("aeroport_depart", "Aeroport depart", "Departure airport"),
    txt("aeroport_arrivee", "Aeroport arrivee", "Arrival airport"),
    num("nb_pieces", "Nombre de colis", "Pieces"),
    num("poids_kg", "Poids (kg)", "Weight (kg)"),
    num("valeur_declaree_xaf", "Valeur declaree", "Declared value"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAirSlot: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "slots",
  tcode: "registre-slots-coordination",
  icon: Icons.Clock,
  titre: "Creneaux aeroportuaires",
  titreEn: "Airport slots",
  description: "Coordination IATA (BABY) des creneaux decollage/atterrissage.",
  descriptionEn: "IATA (BABY) slot coordination for take-off/landing.",
  aide: "Regle 80/20 : sous peine perte historique.",
  aideEn: "Use-it-or-lose-it 80/20 rule.",
  lister: (params) => api.lister("air-slots", params),
  creer: (data) => api.creer("air-slots", data),
  modifier: (id, data) => api.modifier("air-slots", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference slot", "Slot reference"),
    col("aeroport", "Aeroport", "Airport"),
    col("season", "Season IATA", "Season"),
    col("vol_attribue", "Vol attribue", "Flight assigned"),
    col("journee", "Journee", "Weekday"),
    col("heure_obtc", "Heure OBT/C", "OBT/C time"),
    col("slot_historique", "Slot historique", "Grandfathered"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference slot", "Slot reference", { requisCreation: true }),
    txt("aeroport", "Aeroport", "Airport"),
    txt("season", "Season IATA", "Season"),
    txt("vol_attribue", "Vol attribue", "Flight assigned"),
    txt("journee", "Journee", "Weekday"),
    txt("heure_obtc", "Heure OBT/C", "OBT/C time"),
    chk("slot_historique", "Slot historique", "Grandfathered"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreGroundHandlingJob: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "handling",
  tcode: "registre-ground-handling",
  icon: Icons.Package,
  titre: "Traitement au sol",
  titreEn: "Ground handling",
  description: "Prestations au sol : passagers, fret, chargement, ravitaillement.",
  descriptionEn: "Ground services: pax, cargo, load, fuelling.",
  aide: "Facture IH / GH aux compagnies.",
  aideEn: "Handling invoice per flight.",
  lister: (params) => api.lister("air-handling-jobs", params),
  creer: (data) => api.creer("air-handling-jobs", data),
  modifier: (id, data) => api.modifier("air-handling-jobs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vol", "Numero vol", "Flight number"),
    col("aeroport", "Aeroport", "Airport"),
    col("date_traitement", "Date", "Date"),
    col("prestataire", "Prestataire", "Handler"),
    col("nb_pieces_fret", "Pieces fret", "Cargo pieces"),
    col("poids_fret_kg", "Poids fret (kg)", "Cargo weight"),
    col("cout_xaf", "Cout", "Cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vol", "Numero vol", "Flight number"),
    txt("aeroport", "Aeroport", "Airport"),
    dtx("date_traitement", "Date", "Date"),
    txt("prestataire", "Prestataire", "Handler"),
    num("nb_pieces_fret", "Pieces fret", "Cargo pieces"),
    num("poids_fret_kg", "Poids fret (kg)", "Cargo weight"),
    num("cout_xaf", "Cout", "Cost"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreULDInventory: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "uld",
  tcode: "registre-uld-management",
  icon: Icons.Boxes,
  titre: "Parc ULD",
  titreEn: "ULD inventory",
  description: "Conteneurs et palettes aerienes (AKE, PAG, PMC).",
  descriptionEn: "Air containers and pallets (AKE, PAG, PMC).",
  aide: "Tracabilite par numero unique IATA.",
  aideEn: "Unique IATA number tracking.",
  lister: (params) => api.lister("air-uld-inventory", params),
  creer: (data) => api.creer("air-uld-inventory", data),
  modifier: (id, data) => api.modifier("air-uld-inventory", id, data),
  unicite: "numero_uld",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_uld", "Numero ULD", "ULD number"),
    col("type_uld", "Type ULD", "ULD type"),
    col("proprietaire", "Proprietaire", "Owner"),
    col("position_actuelle", "Position actuelle", "Current location"),
    col("etat", "Etat", "Condition"),
    col("date_derniere_inspection", "Derniere inspection", "Last inspection"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_uld", "Numero ULD", "ULD number", { requisCreation: true }),
    txt("type_uld", "Type ULD", "ULD type"),
    txt("proprietaire", "Proprietaire", "Owner"),
    txt("position_actuelle", "Position actuelle", "Current location"),
    txt("etat", "Etat", "Condition"),
    dt("date_derniere_inspection", "Derniere inspection", "Last inspection"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCargoSecurityScreen: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "security",
  tcode: "registre-cargo-security",
  icon: Icons.ScanLine,
  titre: "Sûreté fret arien",
  titreEn: "Air cargo security",
  description: "Screening RC/AC/KC selon reglement (RA, KC, AC statuses).",
  descriptionEn: "Screening per regulated agent / known consignor statuses.",
  aide: "Aucun chargement sans chaine surete complete.",
  aideEn: "No loading without complete security chain.",
  lister: (params) => api.lister("air-cargo-security-screens", params),
  creer: (data) => api.creer("air-cargo-security-screens", data),
  modifier: (id, data) => api.modifier("air-cargo-security-screens", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference screening", "Screening reference"),
    col("numero_awb", "Numero AWB", "AWB number"),
    col("statut_expediteur", "Statut expediteur", "Consignor status"),
    col("methode_screening", "Methode screening", "Screening method"),
    col("date_screening", "Date screening", "Screening date"),
    col("operateur", "Operateur", "Operator"),
    col("resultat", "Resultat", "Result"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference screening", "Screening reference", { requisCreation: true }),
    txt("numero_awb", "Numero AWB", "AWB number"),
    txt("statut_expediteur", "Statut expediteur", "Consignor status"),
    txt("methode_screening", "Methode screening", "Screening method"),
    dtx("date_screening", "Date screening", "Screening date"),
    txt("operateur", "Operateur", "Operator"),
    txt("resultat", "Resultat", "Result"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAirDangerousGoods: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "dgr",
  tcode: "registre-dangerous-goods-air",
  icon: Icons.AlertOctagon,
  titre: "Marchandises dangereuses IATA",
  titreEn: "IATA dangerous goods",
  description: "DGD / etiquette / classe ONU conforme IATA DGR.",
  descriptionEn: "IATA DGD / labels / UN class.",
  aide: "Formation DGR recurrente tous les 2 ans.",
  aideEn: "DGR training every 2 years.",
  lister: (params) => api.lister("air-dangerous-goods", params),
  creer: (data) => api.creer("air-dangerous-goods", data),
  modifier: (id, data) => api.modifier("air-dangerous-goods", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference DGD", "DGD reference"),
    col("numero_awb", "AWB lie", "Linked AWB"),
    col("un_number", "Numero ONU", "UN number"),
    col("classe", "Classe IATA", "Class"),
    col("packaging_group", "Groupe emballage", "Packing group"),
    col("quantite", "Quantite", "Quantity"),
    col("etiquettes", "Etiquettes", "Labels"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference DGD", "DGD reference", { requisCreation: true }),
    txt("numero_awb", "AWB lie", "Linked AWB"),
    txt("un_number", "Numero ONU", "UN number"),
    txt("classe", "Classe IATA", "Class"),
    txt("packaging_group", "Groupe emballage", "Packing group"),
    txt("quantite", "Quantite", "Quantity"),
    txt("etiquettes", "Etiquettes", "Labels"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFlightOperation: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "flightops",
  tcode: "registre-flight-ops",
  icon: Icons.PlaneTakeoff,
  titre: "Operations vol",
  titreEn: "Flight operations",
  description: "Plans de vol, NOTAM, METAR, reserves equipage.",
  descriptionEn: "Flight plans, NOTAM, METAR, crew reserves.",
  aide: "Decision OPE engage la responsabilite commandant.",
  aideEn: "OPE decision binds pilot-in-command.",
  lister: (params) => api.lister("air-flight-operations", params),
  creer: (data) => api.creer("air-flight-operations", data),
  modifier: (id, data) => api.modifier("air-flight-operations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference OPE", "OPE reference"),
    col("numero_vol", "Numero vol", "Flight number"),
    col("aeronef", "Aeronef", "Aircraft"),
    col("aeroport_depart", "Aeroport depart", "Departure airport"),
    col("aeroport_arrivee", "Aeroport arrivee", "Arrival airport"),
    col("date_std", "STD", "STD"),
    col("date_sta", "STA", "STA"),
    col("date_ata", "ATA", "ATA"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference OPE", "OPE reference", { requisCreation: true }),
    txt("numero_vol", "Numero vol", "Flight number"),
    txt("aeronef", "Aeronef", "Aircraft"),
    txt("aeroport_depart", "Aeroport depart", "Departure airport"),
    txt("aeroport_arrivee", "Aeroport arrivee", "Arrival airport"),
    dtx("date_std", "STD", "STD"),
    dtx("date_sta", "STA", "STA"),
    dtx("date_ata", "ATA", "ATA"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCrewRoster: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "crew",
  tcode: "registre-crew-scheduling",
  icon: Icons.Users,
  titre: "Navigation planning",
  titreEn: "Crew scheduling",
  description: "PNT (pilotes), PNC (Cabin), qualification ligne / aeronef.",
  descriptionEn: "Flight deck (PNT), cabin (PNC), type/route qualification.",
  aide: "Repos obligatoire 10h avant report.",
  aideEn: "Mandatory 10h rest before duty.",
  lister: (params) => api.lister("air-crew-rosters", params),
  creer: (data) => api.creer("air-crew-rosters", data),
  modifier: (id, data) => api.modifier("air-crew-rosters", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference tour", "Duty reference"),
    col("nom_membre", "Nom membre", "Member name"),
    col("role", "Role", "Role"),
    col("licence", "Licence", "Licence"),
    col("qualification", "Qualification", "Qualification"),
    col("date_prise_service", "Prise service", "Duty start"),
    col("date_fin_service", "Fin service", "Duty end"),
    col("heures_vol_mois", "Heures vol (mois)", "Monthly flight hours"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference tour", "Duty reference", { requisCreation: true }),
    txt("nom_membre", "Nom membre", "Member name"),
    txt("role", "Role", "Role"),
    txt("licence", "Licence", "Licence"),
    txt("qualification", "Qualification", "Qualification"),
    dtx("date_prise_service", "Prise service", "Duty start"),
    dtx("date_fin_service", "Fin service", "Duty end"),
    num("heures_vol_mois", "Heures vol (mois)", "Monthly flight hours"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAircraftCheck: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "mro",
  tcode: "registre-aircraft-maintenance",
  icon: Icons.Wrench,
  titre: "Maintenance aeronefs (MRO)",
  titreEn: "Aircraft maintenance",
  description: "Checks A/B/C/D, lourdes, AD/SB applicables.",
  descriptionEn: "A/B/C/D checks, heavy, applicable AD/SB.",
  aide: "Cde de maintenance obligatoire apres check C.",
  aideEn: "CofA revalidation mandatory after C check.",
  lister: (params) => api.lister("air-mro-checks", params),
  creer: (data) => api.creer("air-mro-checks", data),
  modifier: (id, data) => api.modifier("air-mro-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference ordre", "Work order reference"),
    col("immatriculation", "Aeronef", "Aircraft"),
    col("type_check", "Type check", "Check type"),
    col("atelier", "Atelier", "Workshop"),
    col("date_debut", "Date debut", "Start date"),
    col("date_fin_prevue", "Fin prevue", "Planned end"),
    col("date_retour_service", "Retour service", "Return to service"),
    col("heures_arret", "Heures AOG", "AOG hours"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference ordre", "Work order reference", { requisCreation: true }),
    txt("immatriculation", "Aeronef", "Aircraft"),
    txt("type_check", "Type check", "Check type"),
    txt("atelier", "Atelier", "Workshop"),
    dt("date_debut", "Date debut", "Start date"),
    dt("date_fin_prevue", "Fin prevue", "Planned end"),
    dt("date_retour_service", "Retour service", "Return to service"),
    num("heures_arret", "Heures AOG", "AOG hours"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAirportCargoWarehouse: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "cargo",
  tcode: "registre-airport-cargo",
  icon: Icons.Building2,
  titre: "Terminal fret aerien",
  titreEn: "Air cargo terminal",
  description: "Magasinage, temperature, zone DCU / surete.",
  descriptionEn: "Storage, temperature, security/Customs zones.",
  aide: "Zone sous surveillance video continue.",
  aideEn: "Zone under continuous CCTV.",
  lister: (params) => api.lister("air-cargo-warehouses", params),
  creer: (data) => api.creer("air-cargo-warehouses", data),
  modifier: (id, data) => api.modifier("air-cargo-warehouses", id, data),
  unicite: "code_entrepot",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_entrepot", "Code entrepot", "Warehouse code"),
    col("aeroport", "Aeroport", "Airport"),
    col("superficie_m2", "Superficie (m2)", "Area (m2)"),
    col("capacite_palettes", "Capacite palettes", "Pallet capacity"),
    col("zones_froides", "Zones froides", "Cold zones"),
    col("zone_douaniere", "Zone douaniere", "Customs zone"),
    col("zone_surete", "Zone surete", "Security zone"),
    col("occupation_pct", "Occupation (%)", "Occupancy (%)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_entrepot", "Code entrepot", "Warehouse code", { requisCreation: true }),
    txt("aeroport", "Aeroport", "Airport"),
    num("superficie_m2", "Superficie (m2)", "Area (m2)"),
    num("capacite_palettes", "Capacite palettes", "Pallet capacity"),
    chk("zones_froides", "Zones froides", "Cold zones"),
    chk("zone_douaniere", "Zone douaniere", "Customs zone"),
    chk("zone_surete", "Zone surete", "Security zone"),
    num("occupation_pct", "Occupation (%)", "Occupancy (%)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAirTariff: ConfigRegistre = {
  permModule: "aerien",
  permSousModule: "tariffs",
  tcode: "registre-air-tariffs",
  icon: Icons.Calculator,
  titre: "Tarification aerienne",
  titreEn: "Air freight tariffs",
  description: "Grille TACT / CDG / surcharges carburant et securite.",
  descriptionEn: "TACT/CDG rate grid + fuel/security surcharges.",
  aide: "Reférence IATA TACT + contrats bilateraux.",
  aideEn: "IATA TACT reference + bilateral agreements.",
  lister: (params) => api.lister("air-tariffs", params),
  creer: (data) => api.creer("air-tariffs", data),
  modifier: (id, data) => api.modifier("air-tariffs", id, data),
  unicite: "code_tarif",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tarif", "Code tarif", "Tariff code"),
    col("origine", "Origine", "Origin"),
    col("destination", "Destination", "Destination"),
    col("poids_min_kg", "Poids min (kg)", "Min weight (kg)"),
    col("type_cargo", "Type cargo", "Cargo type"),
    col("prix_par_kg_xaf", "Prix (XAF/kg)", "Price (XAF/kg)"),
    col("surcharges_xaf", "Surcharges", "Surcharges"),
    col("validite_debut", "Debut validite", "Valid from"),
    col("validite_fin", "Fin validite", "Valid until"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_tarif", "Code tarif", "Tariff code", { requisCreation: true }),
    txt("origine", "Origine", "Origin"),
    txt("destination", "Destination", "Destination"),
    num("poids_min_kg", "Poids min (kg)", "Min weight (kg)"),
    txt("type_cargo", "Type cargo", "Cargo type"),
    num("prix_par_kg_xaf", "Prix (XAF/kg)", "Price (XAF/kg)"),
    num("surcharges_xaf", "Surcharges", "Surcharges"),
    dt("validite_debut", "Debut validite", "Valid from"),
    dt("validite_fin", "Fin validite", "Valid until"),
    txt("statut", "Statut", "Status"),
  ],
};

