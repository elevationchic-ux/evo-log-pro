/**
 * Configs Registre pour portail-technicien (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-technicien");

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

export const registreTechWorkOrder: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "work_order",
  tcode: "registre-work-orders",
  icon: Icons.Wrench,
  titre: "Ordres de travail",
  titreEn: "Work orders",
  description: "Ordre d' intervention recu et execute par le technicien.",
  descriptionEn: "Intervention order received and executed by the technician.",
  aide: "Le kilometrage/moteur justifie le declenchement.",
  aideEn: "Odometer/hour-meter justifies the trigger.",
  lister: (params) => api.lister("tech-work-orders", params),
  creer: (data) => api.creer("tech-work-orders", data),
  modifier: (id, data) => api.modifier("tech-work-orders", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("type_travaux", "Type de travaux", "Work type"),
    col("description", "Description", "Description"),
    col("ouverture", "Ouverture", "Opened"),
    col("cloture", "Cloture", "Closed"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("type_travaux", "Type de travaux", "Work type"),
    txt("description", "Description", "Description"),
    dtx("ouverture", "Ouverture", "Opened"),
    dtx("cloture", "Cloture", "Closed"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechInterventionSheet: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "intervention_sheet",
  tcode: "registre-intervention-sheets",
  icon: Icons.ClipboardCheck,
  titre: "Fiches d' intervention",
  titreEn: "Intervention sheets",
  description: "Compte-rendu detaille d' une intervention realisee.",
  descriptionEn: "Detailed report of a performed intervention.",
  aide: "La main d' oeuvre et la duree tracent l' effort reel.",
  aideEn: "Labor and duration record the real effort.",
  lister: (params) => api.lister("tech-intervention-sheets", params),
  creer: (data) => api.creer("tech-intervention-sheets", data),
  modifier: (id, data) => api.modifier("tech-intervention-sheets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ordre_travail", "Ordre de travail", "Work order"),
    col("technicien", "Technicien", "Technician"),
    col("duree_min", "Duree (min)", "Duration (min)"),
    col("main_oeuvre", "Main d' oeuvre", "Labor cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ordre_travail", "Ordre de travail", "Work order"),
    txt("technicien", "Technicien", "Technician"),
    num("duree_min", "Duree (min)", "Duration (min)"),
    num("main_oeuvre", "Main d' oeuvre", "Labor cost"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechDiagnosis: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "diagnosis",
  tcode: "registre-diagnoses",
  icon: Icons.Stethoscope,
  titre: "Diagnostics",
  titreEn: "Diagnoses",
  description: "Diagnostic technique pose avant reparation.",
  descriptionEn: "Technical diagnosis made before repair.",
  aide: "La cause racine identifiee guide la reparation.",
  aideEn: "The identified root cause guides the repair.",
  lister: (params) => api.lister("tech-diagnoses", params),
  creer: (data) => api.creer("tech-diagnoses", data),
  modifier: (id, data) => api.modifier("tech-diagnoses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("symptome", "Symptome", "Symptom"),
    col("cause_racine", "Cause racine", "Root cause"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("symptome", "Symptome", "Symptom"),
    txt("cause_racine", "Cause racine", "Root cause"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechPartConsumption: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "part_consumption",
  tcode: "registre-parts-consumption",
  icon: Icons.Package,
  titre: "Consommation de pieces",
  titreEn: "Parts consumption",
  description: "Pieces detachees posees lors d' une intervention.",
  descriptionEn: "Spare parts fitted during an intervention.",
  aide: "La quantite et la reference engageent le stock.",
  aideEn: "Quantity and reference commit the stock.",
  lister: (params) => api.lister("tech-parts-consumption", params),
  creer: (data) => api.creer("tech-parts-consumption", data),
  modifier: (id, data) => api.modifier("tech-parts-consumption", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ordre_travail", "Ordre de travail", "Work order"),
    col("piece", "Piece", "Part"),
    col("quantite", "Quantite", "Quantity"),
    col("cout_unitaire", "Cout unitaire", "Unit cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ordre_travail", "Ordre de travail", "Work order"),
    txt("piece", "Piece", "Part"),
    num("quantite", "Quantite", "Quantity"),
    num("cout_unitaire", "Cout unitaire", "Unit cost"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechPreventivePlan: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "preventive_plan",
  tcode: "registre-preventive-plans",
  icon: Icons.CalendarCheck,
  titre: "Plans d' entretien preventif",
  titreEn: "Preventive plans",
  description: "Echeancier d' entretien planifie d' un vehicule.",
  descriptionEn: "Scheduled maintenance calendar of a vehicle.",
  aide: "L' intervalle (km ou jours) determine la prochaine echeance.",
  aideEn: "The interval (km or days) sets the next due date.",
  lister: (params) => api.lister("tech-preventive-plans", params),
  creer: (data) => api.creer("tech-preventive-plans", data),
  modifier: (id, data) => api.modifier("tech-preventive-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("operation", "Operation", "Operation"),
    col("intervalle_km", "Intervalle (km)", "Interval (km)"),
    col("derniere_realisation", "Derniere realization", "Last done"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("operation", "Operation", "Operation"),
    num("intervalle_km", "Intervalle (km)", "Interval (km)"),
    dt("derniere_realisation", "Derniere realization", "Last done"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechBreakdownTicket: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "breakdown_ticket",
  tcode: "registre-breakdown-tickets",
  icon: Icons.AlertTriangle,
  titre: "Billets de panne",
  titreEn: "Breakdown tickets",
  description: "Signalement de panne transmis au technicien.",
  descriptionEn: "Breakdown report routed to the technician.",
  aide: "La severite priorise la prise en charge.",
  aideEn: "Severity prioritizes the response.",
  lister: (params) => api.lister("tech-breakdown-tickets", params),
  creer: (data) => api.creer("tech-breakdown-tickets", data),
  modifier: (id, data) => api.modifier("tech-breakdown-tickets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("lieu", "Lieu", "Location"),
    col("severite", "Severite", "Severity"),
    col("recu", "Recu", "Received"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("lieu", "Lieu", "Location"),
    txt("severite", "Severite", "Severity"),
    dtx("recu", "Recu", "Received"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechRepairReport: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "repair_report",
  tcode: "registre-repair-reports",
  icon: Icons.FileText,
  titre: "Rapports de reparation",
  titreEn: "Repair reports",
  description: "Bilan de fin de reparation et remise en service.",
  descriptionEn: "End-of-repair summary and return to service.",
  aide: "Le test de sortie certifie la remise en service.",
  aideEn: "The exit test certifies the return to service.",
  lister: (params) => api.lister("tech-repair-reports", params),
  creer: (data) => api.creer("tech-repair-reports", data),
  modifier: (id, data) => api.modifier("tech-repair-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ordre_travail", "Ordre de travail", "Work order"),
    col("travaux_realises", "Travaux realises", "Work performed"),
    col("test_sortie_ok", "Test de sortie OK", "Exit test OK"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ordre_travail", "Ordre de travail", "Work order"),
    txt("travaux_realises", "Travaux realises", "Work performed"),
    chk("test_sortie_ok", "Test de sortie OK", "Exit test OK"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechCalibrationRecord: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "calibration_record",
  tcode: "registre-calibration-records",
  icon: Icons.Ruler,
  titre: "Fiches d' etalonnage",
  titreEn: "Calibration records",
  description: "Etalonnage d' un instrument de mesure du parc.",
  descriptionEn: "Calibration of a fleet measuring instrument.",
  aide: "La tolerance et la prochaine date encadrent la validite.",
  aideEn: "Tolerance and next date bound validity.",
  lister: (params) => api.lister("tech-calibration-records", params),
  creer: (data) => api.creer("tech-calibration-records", data),
  modifier: (id, data) => api.modifier("tech-calibration-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("instrument", "Instrument", "Instrument"),
    col("tolerance", "Tolerance", "Tolerance"),
    col("date_etalonnage", "Date etalonnage", "Calibration date"),
    col("prochaine_date", "Prochaine echeance", "Next due"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("instrument", "Instrument", "Instrument"),
    txt("tolerance", "Tolerance", "Tolerance"),
    dt("date_etalonnage", "Date etalonnage", "Calibration date"),
    dt("prochaine_date", "Prochaine echeance", "Next due"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechEquipmentChecklist: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "equipment_checklist",
  tcode: "registre-equipment-checklists",
  icon: Icons.ListChecks,
  titre: "Controles d' equipement atelier",
  titreEn: "Equipment checklists",
  description: "Checklist de verification d' un equipement d' atelier.",
  descriptionEn: "Verification checklist of a workshop equipment.",
  aide: "Un point en defaut rend l' equipement indisponible.",
  aideEn: "A failed point makes the equipment unavailable.",
  lister: (params) => api.lister("tech-equipment-checklists", params),
  creer: (data) => api.creer("tech-equipment-checklists", data),
  modifier: (id, data) => api.modifier("tech-equipment-checklists", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("equipement", "Equipement", "Equipment"),
    col("points_controles", "Points controles", "Points checked"),
    col("anomalies", "Anomalies", "Defects"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("equipement", "Equipement", "Equipment"),
    num("points_controles", "Points controles", "Points checked"),
    num("anomalies", "Anomalies", "Defects"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechToolLoan: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "tool_loan",
  tcode: "registre-tool-loans",
  icon: Icons.Hammer,
  titre: "Prets d' outillage",
  titreEn: "Tool loans",
  description: "Sortie et retour d' outillage par le technicien.",
  descriptionEn: "Tool issue and return by the technician.",
  aide: "Le retour non enregistre bloque l' inventaire d' outillage.",
  aideEn: "An unlogged return blocks the tool inventory.",
  lister: (params) => api.lister("tech-tool-loans", params),
  creer: (data) => api.creer("tech-tool-loans", data),
  modifier: (id, data) => api.modifier("tech-tool-loans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("outil", "Outil", "Tool"),
    col("technicien", "Technicien", "Technician"),
    col("sortie", "Sortie", "Issued"),
    col("retour", "Retour", "Returned"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("outil", "Outil", "Tool"),
    txt("technicien", "Technicien", "Technician"),
    dtx("sortie", "Sortie", "Issued"),
    dtx("retour", "Retour", "Returned"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechSafetyLockout: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "safety_lockout",
  tcode: "registre-safety-lockouts",
  icon: Icons.Lock,
  titre: "Consignations de securite",
  titreEn: "Safety lockouts",
  description: "Consignation (LOTO) d' une installation avant intervention.",
  descriptionEn: "Lock-out/tag-out of an installation before intervention.",
  aide: "L' autorisation de levee engage le responsable.",
  aideEn: "The release authorization commits the responsible person.",
  lister: (params) => api.lister("tech-safety-lockouts", params),
  creer: (data) => api.creer("tech-safety-lockouts", data),
  modifier: (id, data) => api.modifier("tech-safety-lockouts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("installation", "Installation", "Installation"),
    col("motif", "Motif", "Reason"),
    col("pose", "Pose", "Applied"),
    col("levee", "Levee", "Released"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("installation", "Installation", "Installation"),
    txt("motif", "Motif", "Reason"),
    dtx("pose", "Pose", "Applied"),
    dtx("levee", "Levee", "Released"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechWarrantyClaim: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "warranty_claim",
  tcode: "registre-warranty-claims",
  icon: Icons.BadgeCheck,
  titre: "Reclamations de garantie",
  titreEn: "Warranty claims",
  description: "Demande de prise en charge sous garantie d' une piece.",
  descriptionEn: "Request to cover a part under warranty.",
  aide: "Le numero de serie et la date d' achat conditionnent l' admissibilite.",
  aideEn: "Serial number and purchase date condition admissibility.",
  lister: (params) => api.lister("tech-warranty-claims", params),
  creer: (data) => api.creer("tech-warranty-claims", data),
  modifier: (id, data) => api.modifier("tech-warranty-claims", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("piece", "Piece", "Part"),
    col("fournisseur", "Fournisseur", "Supplier"),
    col("date_achat", "Date d' achat", "Purchase date"),
    col("montant", "Montant", "Amount"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("piece", "Piece", "Part"),
    txt("fournisseur", "Fournisseur", "Supplier"),
    dt("date_achat", "Date d' achat", "Purchase date"),
    num("montant", "Montant", "Amount"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechServiceAppointment: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "service_appointment",
  tcode: "registre-service-appointments",
  icon: Icons.CalendarDays,
  titre: "RDV d' atelier",
  titreEn: "Service appointments",
  description: "Creneau planifie pour une intervention en atelier.",
  descriptionEn: "Scheduled slot for a workshop intervention.",
  aide: "Le créneau reserve immobilise le vehicule a une date donnee.",
  aideEn: "The booked slot grounds the vehicle on a given date.",
  lister: (params) => api.lister("tech-service-appointments", params),
  creer: (data) => api.creer("tech-service-appointments", data),
  modifier: (id, data) => api.modifier("tech-service-appointments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("creneau", "Creneau", "Slot"),
    col("atelier", "Atelier", "Workshop"),
    col("duree_min", "Duree (min)", "Duration (min)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    dtx("creneau", "Creneau", "Slot"),
    txt("atelier", "Atelier", "Workshop"),
    num("duree_min", "Duree (min)", "Duration (min)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechLaborTimesheet: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "labor_timesheet",
  tcode: "registre-labor-timesheets",
  icon: Icons.Timer,
  titre: "Feuilles de temps main d' oeuvre",
  titreEn: "Labor timesheets",
  description: "Temps passe par le technicien sur chaque ordre.",
  descriptionEn: "Time spent by the technician on each order.",
  aide: "Le temps declare alimente le cout de main d' oeuvre.",
  aideEn: "Logged time feeds the labor cost.",
  lister: (params) => api.lister("tech-labor-timesheets", params),
  creer: (data) => api.creer("tech-labor-timesheets", data),
  modifier: (id, data) => api.modifier("tech-labor-timesheets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ordre_travail", "Ordre de travail", "Work order"),
    col("technicien", "Technicien", "Technician"),
    col("minutes", "Minutes", "Minutes"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ordre_travail", "Ordre de travail", "Work order"),
    txt("technicien", "Technicien", "Technician"),
    num("minutes", "Minutes", "Minutes"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechUpgradeRequest: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "upgrade_request",
  tcode: "registre-upgrade-requests",
  icon: Icons.TrendingUp,
  titre: "Demandes d' amlioration",
  titreEn: "Upgrade requests",
  description: "Demande d' amlioration technique sur un vehicule ou un equipement.",
  descriptionEn: "Technical improvement request on a vehicle or equipment.",
  aide: "Le gain attendu justifie l' investissement.",
  aideEn: "The expected gain justifies the investment.",
  lister: (params) => api.lister("tech-upgrade-requests", params),
  creer: (data) => api.creer("tech-upgrade-requests", data),
  modifier: (id, data) => api.modifier("tech-upgrade-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("cible", "Cible", "Target"),
    col("objet", "Objet", "Object"),
    col("gain_attendu", "Gain attendu", "Expected gain"),
    col("cout_estime", "Cout estime", "Estimated cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("cible", "Cible", "Target"),
    txt("objet", "Objet", "Object"),
    txt("gain_attendu", "Gain attendu", "Expected gain"),
    num("cout_estime", "Cout estime", "Estimated cost"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechFailureAnalysis: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "failure_analysis",
  tcode: "registre-failure-analyses",
  icon: Icons.Microscope,
  titre: "Analyses de panne",
  titreEn: "Failure analyses",
  description: "Analyse des causes d' une panne repetitive ou critique.",
  descriptionEn: "Root-cause analysis of a recurring or critical failure.",
  aide: "La frequence et la criticite priorisent l' action preventive.",
  aideEn: "Frequency and criticality prioritize the preventive action.",
  lister: (params) => api.lister("tech-failure-analyses", params),
  creer: (data) => api.creer("tech-failure-analyses", data),
  modifier: (id, data) => api.modifier("tech-failure-analyses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("mode_defaillance", "Mode de defaillance", "Failure mode"),
    col("frequence", "Frequence", "Frequency"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("mode_defaillance", "Mode de defaillance", "Failure mode"),
    num("frequence", "Frequence", "Frequency"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechSpareRequest: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "spare_request",
  tcode: "registre-spare-requests",
  icon: Icons.Boxes,
  titre: "Demandes de pieces",
  titreEn: "Spare requests",
  description: "Demande de reapprovisionnement de pieces pour l' atelier.",
  descriptionEn: "Restocking request of parts for the workshop.",
  aide: "Le stock bas declenche la demande au magasin.",
  aideEn: "Low stock triggers the request to the store.",
  lister: (params) => api.lister("tech-spare-requests", params),
  creer: (data) => api.creer("tech-spare-requests", data),
  modifier: (id, data) => api.modifier("tech-spare-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("piece", "Piece", "Part"),
    col("quantite", "Quantite", "Quantity"),
    col("demandeur", "Demandeur", "Requester"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("piece", "Piece", "Part"),
    num("quantite", "Quantite", "Quantity"),
    txt("demandeur", "Demandeur", "Requester"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechInspectionRecord: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "inspection_record",
  tcode: "registre-inspection-records",
  icon: Icons.ClipboardList,
  titre: "Fiches de controle technique",
  titreEn: "Inspection records",
  description: "Controle technique / reglementaire d' un vehicule.",
  descriptionEn: "Technical / regulatory inspection of a vehicle.",
  aide: "La date de validite conditionne la circulation.",
  aideEn: "Validity date conditions circulation.",
  lister: (params) => api.lister("tech-inspection-records", params),
  creer: (data) => api.creer("tech-inspection-records", data),
  modifier: (id, data) => api.modifier("tech-inspection-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("vehicule", "Vehicule", "Vehicle"),
    col("type_controle", "Type de controle", "Inspection type"),
    col("date_controle", "Date controle", "Inspection date"),
    col("validite", "Validite", "Validity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("vehicule", "Vehicule", "Vehicle"),
    txt("type_controle", "Type de controle", "Inspection type"),
    dt("date_controle", "Date controle", "Inspection date"),
    dt("validite", "Validite", "Validity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTechWorkOrderCost: ConfigRegistre = {
  permModule: "parc",
  permSousModule: "work_order_cost",
  tcode: "registre-work-order-costs",
  icon: Icons.CircleDollarSign,
  titre: "Couts d' ordre de travail",
  titreEn: "Work order costs",
  description: "Imputation des couts (pieces + MO) d' un ordre de travail.",
  descriptionEn: "Cost posting (parts + labor) of a work order.",
  aide: "La somme pieces + MO doit egaler le cout total facture.",
  aideEn: "Parts plus labor must equal the billed total.",
  lister: (params) => api.lister("tech-work-order-costs", params),
  creer: (data) => api.creer("tech-work-order-costs", data),
  modifier: (id, data) => api.modifier("tech-work-order-costs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ordre_travail", "Ordre de travail", "Work order"),
    col("cout_pieces", "Cout pieces", "Parts cost"),
    col("cout_mo", "Cout main d' oeuvre", "Labor cost"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ordre_travail", "Ordre de travail", "Work order"),
    num("cout_pieces", "Cout pieces", "Parts cost"),
    num("cout_mo", "Cout main d' oeuvre", "Labor cost"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

