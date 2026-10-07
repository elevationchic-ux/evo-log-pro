/**
 * Configs Registre pour portail-chauffeur (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-chauffeur");

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

export const registreChfTripSheet: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "trip_sheet",
  tcode: "registre-trip-sheets",
  icon: Icons.Route,
  titre: "Feuilles de route",
  titreEn: "Trip sheets",
  description: "Enregistrements de parcours reellement effectues par le chauffeur.",
  descriptionEn: "Actual routes performed by the driver.",
  aide: "Km de debut/fin justifient la distance reellement parcourue.",
  aideEn: "Start/end odometer justify the actual distance.",
  lister: (params) => api.lister("chf-trip-sheets", params),
  creer: (data) => api.creer("chf-trip-sheets", data),
  modifier: (id, data) => api.modifier("chf-trip-sheets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("mission", "Mission", "Mission"),
    col("debut", "Debut", "Start"),
    col("fin", "Fin", "End"),
    col("km_debut", "Km debut", "Start odometer"),
    col("km_fin", "Km fin", "End odometer"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("mission", "Mission", "Mission"),
    dtx("debut", "Debut", "Start"),
    dtx("fin", "Fin", "End"),
    num("km_debut", "Km debut", "Start odometer"),
    num("km_fin", "Km fin", "End odometer"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfDailyVehicleCheck: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "daily_vehicle_check",
  tcode: "registre-daily-vehicle-checks",
  icon: Icons.ClipboardCheck,
  titre: "Controles quotidiens du vehicule",
  titreEn: "Daily vehicle checks",
  description: "Checklist de securite avant depart.",
  descriptionEn: "Pre-departure safety checklist.",
  aide: "Les anomalies bloquent le depart jusqu' a resolution.",
  aideEn: "Defects block departure until resolved.",
  lister: (params) => api.lister("chf-daily-vehicle-checks", params),
  creer: (data) => api.creer("chf-daily-vehicle-checks", data),
  modifier: (id, data) => api.modifier("chf-daily-vehicle-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("date_controle", "Date controle", "Check date"),
    col("points_controles", "Points controles", "Points checked"),
    col("anomalies", "Anomalies", "Defects"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    dtx("date_controle", "Date controle", "Check date"),
    num("points_controles", "Points controles", "Points checked"),
    chk("anomalies", "Anomalies", "Defects"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfFuelLog: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "fuel_log",
  tcode: "registre-fuel-logs",
  icon: Icons.Fuel,
  titre: "Carnet carburant",
  titreEn: "Fuel logs",
  description: "Pleins effectues par le chauffeur.",
  descriptionEn: "Fuel-ups performed by the driver.",
  aide: "Litres et prix justifient la consommation.",
  aideEn: "Liters and price justify consumption.",
  lister: (params) => api.lister("chf-fuel-logs", params),
  creer: (data) => api.creer("chf-fuel-logs", data),
  modifier: (id, data) => api.modifier("chf-fuel-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("litres", "Litres", "Liters"),
    col("prix", "Prix", "Amount"),
    col("station", "Station", "Station"),
    col("date_plein", "Date plein", "Fill date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    num("litres", "Litres", "Liters"),
    num("prix", "Prix", "Amount"),
    txt("station", "Station", "Station"),
    dtx("date_plein", "Date plein", "Fill date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfDrivingTimeRecord: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "driving_time",
  tcode: "registre-driving-times",
  icon: Icons.Timer,
  titre: "Temps de conduite",
  titreEn: "Driving times",
  description: "Durees de conduite brutes (chronotachygraphe).",
  descriptionEn: "Raw driving durations (tachograph).",
  aide: "Depassement du seuil legal = statut HORS_REGLE.",
  aideEn: "Exceeding the legal limit = out-of-regulation.",
  lister: (params) => api.lister("chf-driving-times", params),
  creer: (data) => api.creer("chf-driving-times", data),
  modifier: (id, data) => api.modifier("chf-driving-times", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("chauffeur", "Chauffeur", "Driver"),
    col("debut", "Debut", "Start"),
    col("fin", "Fin", "End"),
    col("minutes_conduite", "Minutes de conduite", "Driving minutes"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("chauffeur", "Chauffeur", "Driver"),
    dtx("debut", "Debut", "Start"),
    dtx("fin", "Fin", "End"),
    num("minutes_conduite", "Minutes de conduite", "Driving minutes"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfRestBreak: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "rest_break",
  tcode: "registre-rest-breaks",
  icon: Icons.Coffee,
  titre: "Pauses et repos",
  titreEn: "Rest breaks",
  description: "Repos obligaires pris par le chauffeur.",
  descriptionEn: "Mandatory rest taken by the driver.",
  aide: "La duree et le lieu attestent le respect de la reglementation.",
  aideEn: "Duration and place evidence regulatory compliance.",
  lister: (params) => api.lister("chf-rest-breaks", params),
  creer: (data) => api.creer("chf-rest-breaks", data),
  modifier: (id, data) => api.modifier("chf-rest-breaks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("chauffeur", "Chauffeur", "Driver"),
    col("debut", "Debut", "Start"),
    col("duree_min", "Duree (min)", "Duration (min)"),
    col("lieu", "Lieu", "Place"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("chauffeur", "Chauffeur", "Driver"),
    dtx("debut", "Debut", "Start"),
    num("duree_min", "Duree (min)", "Duration (min)"),
    txt("lieu", "Lieu", "Place"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfTollReceipt: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "toll_receipt",
  tcode: "registre-toll-receipts",
  icon: Icons.Receipt,
  titre: "Recus de peage",
  titreEn: "Toll receipts",
  description: "Frais de peage engages sur la route.",
  descriptionEn: "Toll costs incurred on the road.",
  aide: "Le montant et le troncon justifiant la note de frais.",
  aideEn: "Amount and section justify the expense.",
  lister: (params) => api.lister("chf-toll-receipts", params),
  creer: (data) => api.creer("chf-toll-receipts", data),
  modifier: (id, data) => api.modifier("chf-toll-receipts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("peage", "Peage", "Toll booth"),
    col("montant", "Montant", "Amount"),
    col("date_passage", "Date passage", "Crossing date"),
    col("troncon", "Troncon", "Section"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("peage", "Peage", "Toll booth"),
    num("montant", "Montant", "Amount"),
    dtx("date_passage", "Date passage", "Crossing date"),
    txt("troncon", "Troncon", "Section"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfParkingSession: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "parking_session",
  tcode: "registre-parking-sessions",
  icon: Icons.Building2,
  titre: "Sessions de parking",
  titreEn: "Parking sessions",
  description: "Arrets decharge / fourriere / parking payant.",
  descriptionEn: "Unloading / impound / paid parking.",
  aide: "Entree et sortie determinent la duree et le frais.",
  aideEn: "Entry and exit determine duration and cost.",
  lister: (params) => api.lister("chf-parking-sessions", params),
  creer: (data) => api.creer("chf-parking-sessions", data),
  modifier: (id, data) => api.modifier("chf-parking-sessions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("lieu", "Lieu", "Place"),
    col("entree", "Entree", "Entry"),
    col("sortie", "Sortie", "Exit"),
    col("frais", "Frais", "Cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("lieu", "Lieu", "Place"),
    dtx("entree", "Entree", "Entry"),
    dtx("sortie", "Sortie", "Exit"),
    num("frais", "Frais", "Cost"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfCargoSeal: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "cargo_seal",
  tcode: "registre-cargo-seals",
  icon: Icons.Lock,
  titre: "Plombs de cargaison",
  titreEn: "Cargo seals",
  description: "Pose et verification des plombs sur unite de transport.",
  descriptionEn: "Seal placement and check on the transport unit.",
  aide: "Plomb intact a l' arrivee = cargo nonouvert.",
  aideEn: "Intact seal at arrival = cargo unopened.",
  lister: (params) => api.lister("chf-cargo-seals", params),
  creer: (data) => api.creer("chf-cargo-seals", data),
  modifier: (id, data) => api.modifier("chf-cargo-seals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("unite", "Unite", "Unit"),
    col("numero_plomb", "Numero de plomb", "Seal number"),
    col("pose_datetime", "Pose", "Sealed at"),
    col("retrait_datetime", "Retrait", "Removed at"),
    col("intact", "Intact", "Intact"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("unite", "Unite", "Unit"),
    txt("numero_plomb", "Numero de plomb", "Seal number"),
    dtx("pose_datetime", "Pose", "Sealed at"),
    dtx("retrait_datetime", "Retrait", "Removed at"),
    chk("intact", "Intact", "Intact"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfRoadsideIncident: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "roadside_incident",
  tcode: "registre-roadside-incidents",
  icon: Icons.AlertTriangle,
  titre: "Incidents de route",
  titreEn: "Roadside incidents",
  description: "Evenement inattendu survenu en conduite.",
  descriptionEn: "Unexpected event during driving.",
  aide: "Gravite et localisation qualifient l' incident.",
  aideEn: "Severity and location qualify it.",
  lister: (params) => api.lister("chf-roadside-incidents", params),
  creer: (data) => api.creer("chf-roadside-incidents", data),
  modifier: (id, data) => api.modifier("chf-roadside-incidents", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("type_incident", "Type", "Type"),
    col("localisation", "Localisation", "Location"),
    col("date", "Date", "Date"),
    col("gravite", "Gravite", "Severity"),
    col("decrit", "Description", "Description"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("type_incident", "Type", "Type"),
    txt("localisation", "Localisation", "Location"),
    dtx("date", "Date", "Date"),
    txt("gravite", "Gravite", "Severity"),
    txt("decrit", "Description", "Description"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfDeliveryStop: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "delivery_stop",
  tcode: "registre-delivery-stops",
  icon: Icons.MapPin,
  titre: "Points de livraison",
  titreEn: "Delivery stops",
  description: "Escales de livraison d' une tournee.",
  descriptionEn: "Delivery points of a route.",
  aide: "L' ordre structure le sequence de tournee.",
  aideEn: "The order drives route sequencing.",
  lister: (params) => api.lister("chf-delivery-stops", params),
  creer: (data) => api.creer("chf-delivery-stops", data),
  modifier: (id, data) => api.modifier("chf-delivery-stops", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tournee", "Tournee", "Route"),
    col("adresse", "Adresse", "Address"),
    col("ordre", "Ordre", "Order"),
    col("arrivee", "Arrivee", "Arrival"),
    col("departure", "Depart", "Departure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("tournee", "Tournee", "Route"),
    txt("adresse", "Adresse", "Address"),
    num("ordre", "Ordre", "Order"),
    dtx("arrivee", "Arrivee", "Arrival"),
    dtx("departure", "Depart", "Departure"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfMileageLog: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "mileage_log",
  tcode: "registre-mileage-logs",
  icon: Icons.Gauge,
  titre: "Releves de kilometrage",
  titreEn: "Mileage logs",
  description: "Releve compteur kilometrique par le chauffeur.",
  descriptionEn: "Odometer reading by the driver.",
  aide: "La difference entre deux releves donne la distance.",
  aideEn: "Delta between two reads gives distance.",
  lister: (params) => api.lister("chf-mileage-logs", params),
  creer: (data) => api.creer("chf-mileage-logs", data),
  modifier: (id, data) => api.modifier("chf-mileage-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("date", "Date", "Date"),
    col("km_debut", "Km debut", "Start odometer"),
    col("km_fin", "Km fin", "End odometer"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    dtx("date", "Date", "Date"),
    num("km_debut", "Km debut", "Start odometer"),
    num("km_fin", "Km fin", "End odometer"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfLoadSecuringCheck: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "load_securing_check",
  tcode: "registre-load-securing-checks",
  icon: Icons.Anchor,
  titre: "Controles d' arrimage",
  titreEn: "Load securing checks",
  description: "Verification de la fixation et repartition de charge.",
  descriptionEn: "Check of cargo fixation and weight distribution.",
  aide: "Sangles et equilibre conditionnent l' autorisation de depart.",
  aideEn: "Straps and balance gate the go-ahead.",
  lister: (params) => api.lister("chf-load-securing-checks", params),
  creer: (data) => api.creer("chf-load-securing-checks", data),
  modifier: (id, data) => api.modifier("chf-load-securing-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("unite", "Unite", "Unit"),
    col("sangles_ok", "Sangles OK", "Straps OK"),
    col("poids_equilibre", "Poids / equilibre", "Weight / balance"),
    col("controle_datetime", "Controle", "Checked at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("unite", "Unite", "Unit"),
    chk("sangles_ok", "Sangles OK", "Straps OK"),
    txt("poids_equilibre", "Poids / equilibre", "Weight / balance"),
    dtx("controle_datetime", "Controle", "Checked at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfBorderCrossing: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "border_crossing",
  tcode: "registre-border-crossings",
  icon: Icons.Flag,
  titre: "Postes frontiere",
  titreEn: "Border crossings",
  description: "Traversees de frontiere avec controle documentaire.",
  descriptionEn: "Border transits with document control.",
  aide: "Documents OK conditionne le passage.",
  aideEn: "Documents OK gates the crossing.",
  lister: (params) => api.lister("chf-border-crossings", params),
  creer: (data) => api.creer("chf-border-crossings", data),
  modifier: (id, data) => api.modifier("chf-border-crossings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("poste", "Poste", "Post"),
    col("pays", "Pays", "Country"),
    col("entree_sortie", "Entree / sortie", "Entry / exit"),
    col("horodatage", "Horodatage", "Timestamp"),
    col("documents_ok", "Documents OK", "Documents OK"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("poste", "Poste", "Post"),
    txt("pays", "Pays", "Country"),
    txt("entree_sortie", "Entree / sortie", "Entry / exit"),
    dtx("horodatage", "Horodatage", "Timestamp"),
    chk("documents_ok", "Documents OK", "Documents OK"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfDeliveryAppointment: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "delivery_appointment",
  tcode: "registre-delivery-appointments",
  icon: Icons.CalendarClock,
  titre: "RDV de livraison",
  titreEn: "Delivery appointments",
  description: "Creneau convenu avec le destinataire.",
  descriptionEn: "Slot agreed with the consignee.",
  aide: "Le respect du creneau evite les retours.",
  aideEn: "Keeping the slot avoids returns.",
  lister: (params) => api.lister("chf-delivery-appointments", params),
  creer: (data) => api.creer("chf-delivery-appointments", data),
  modifier: (id, data) => api.modifier("chf-delivery-appointments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("creneau", "Creneau", "Slot"),
    col("site", "Site", "Site"),
    col("contact", "Contact", "Contact"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    dtx("creneau", "Creneau", "Slot"),
    txt("site", "Site", "Site"),
    txt("contact", "Contact", "Contact"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfPpeIssue: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "ppe_issue",
  tcode: "registre-ppe-issues",
  icon: Icons.ShieldCheck,
  titre: "Remise d' EPI",
  titreEn: "PPE issues",
  description: "Dotation d' equipements de protection individuelle.",
  descriptionEn: "Provision of personal protective equipment.",
  aide: "L' etat et la date attestent la mise a disposition.",
  aideEn: "Condition and date evidence the provision.",
  lister: (params) => api.lister("chf-ppe-issues", params),
  creer: (data) => api.creer("chf-ppe-issues", data),
  modifier: (id, data) => api.modifier("chf-ppe-issues", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("equipement", "Equipement", "Equipment"),
    col("taille", "Taille", "Size"),
    col("date_remise", "Date remise", "Issue date"),
    col("etat", "Etat", "Condition"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("equipement", "Equipement", "Equipment"),
    txt("taille", "Taille", "Size"),
    dt("date_remise", "Date remise", "Issue date"),
    txt("etat", "Etat", "Condition"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfShiftHandover: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "shift_handover",
  tcode: "registre-shift-handovers",
  icon: Icons.ArrowLeftRight,
  titre: "Relais de conduite",
  titreEn: "Shift handovers",
  description: "Passation entre deux chauffeurs sur la meme unite.",
  descriptionEn: "Handover between two drivers on the same unit.",
  aide: "Les consignes passees engagent le reprenant.",
  aideEn: "Passed instructions bind the reliever.",
  lister: (params) => api.lister("chf-shift-handovers", params),
  creer: (data) => api.creer("chf-shift-handovers", data),
  modifier: (id, data) => api.modifier("chf-shift-handovers", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("sortant", "Chauffeur sortant", "Outgoing driver"),
    col("entrant", "Chauffeur entrant", "Incoming driver"),
    col("datetime", "Date relais", "Handover date"),
    col("consignes", "Consignes", "Instructions"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("sortant", "Chauffeur sortant", "Outgoing driver"),
    txt("entrant", "Chauffeur entrant", "Incoming driver"),
    dtx("datetime", "Date relais", "Handover date"),
    txt("consignes", "Consignes", "Instructions"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfBreakdownReport: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "breakdown_report",
  tcode: "registre-breakdown-reports",
  icon: Icons.Wrench,
  titre: "Signalements de panne",
  titreEn: "Breakdown reports",
  description: "Declaration d' une panne vehicule par le chauffeur.",
  descriptionEn: "Driver's report of a vehicle breakdown.",
  aide: "L' immobilisation declenche le remorquage / reassignation.",
  aideEn: "Immobilization triggers towing / reassignment.",
  lister: (params) => api.lister("chf-breakdown-reports", params),
  creer: (data) => api.creer("chf-breakdown-reports", data),
  modifier: (id, data) => api.modifier("chf-breakdown-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("panne", "Panne", "Breakdown"),
    col("lieu", "Lieu", "Place"),
    col("date_signalement", "Signalement", "Report date"),
    col("immobilise", "Immobilise", "Immobilized"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("panne", "Panne", "Breakdown"),
    txt("lieu", "Lieu", "Place"),
    dtx("date_signalement", "Signalement", "Report date"),
    chk("immobilise", "Immobilise", "Immobilized"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfTyreCheck: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "tyre_check",
  tcode: "registre-tyre-checks",
  icon: Icons.Disc,
  titre: "Controles pneumatiques",
  titreEn: "Tyre checks",
  description: "Releve de pression et usure par essieu.",
  descriptionEn: "Pressure and wear reading per axle.",
  aide: "Pression et usure hors tolérance = a intervenir.",
  aideEn: "Out-of-tolerance pressure/wear requires action.",
  lister: (params) => api.lister("chf-tyre-checks", params),
  creer: (data) => api.creer("chf-tyre-checks", data),
  modifier: (id, data) => api.modifier("chf-tyre-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("numero_essieu", "Numero d' essieu", "Axle number"),
    col("pression_bar", "Pression (bar)", "Pressure (bar)"),
    col("usure_mm", "Usure (mm)", "Tread (mm)"),
    col("date_controle", "Controle", "Checked at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    num("numero_essieu", "Numero d' essieu", "Axle number"),
    num("pression_bar", "Pression (bar)", "Pressure (bar)"),
    num("usure_mm", "Usure (mm)", "Tread (mm)"),
    dtx("date_controle", "Controle", "Checked at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChfCargoPhoto: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "cargo_photo",
  tcode: "registre-cargo-photos",
  icon: Icons.Camera,
  titre: "Photos de cargaison",
  titreEn: "Cargo photos",
  description: "Photo etat de la marchandise (chargement / livraison).",
  descriptionEn: "Condition photo of the goods (loading / delivery).",
  aide: "La photo atteste de l' etat au moment de la prise.",
  aideEn: "The photo evidences condition at capture time.",
  lister: (params) => api.lister("chf-cargo-photos", params),
  creer: (data) => api.creer("chf-cargo-photos", data),
  modifier: (id, data) => api.modifier("chf-cargo-photos", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("mission", "Mission", "Mission"),
    col("prise", "Prise", "Captured at"),
    col("legende", "Legende", "Caption"),
    col("fichier", "Fichier", "File"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("mission", "Mission", "Mission"),
    dtx("prise", "Prise", "Captured at"),
    txt("legende", "Legende", "Caption"),
    txt("fichier", "Fichier", "File"),
    txt("statut", "Statut", "Status"),
  ],
};

