/**
 * Configs Registre pour portail-collaborateur (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-collaborateur");

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

export const registreCollAssignment: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "assignment_record",
  tcode: "registre-assignment-records",
  icon: Icons.Briefcase,
  titre: "Affectations de mission",
  titreEn: "Assignment records",
  description: "Affectation d' un collaborateur a une mission / un site.",
  descriptionEn: "Assignment of a collaborator to a mission / site.",
  aide: "La periode et le responsable encadrent l' affectation.",
  aideEn: "Period and manager bound the assignment.",
  lister: (params) => api.lister("coll-assignment-records", params),
  creer: (data) => api.creer("coll-assignment-records", data),
  modifier: (id, data) => api.modifier("coll-assignment-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("mission", "Mission", "Mission"),
    col("site", "Site", "Site"),
    col("debut", "Debut", "Start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("mission", "Mission", "Mission"),
    txt("site", "Site", "Site"),
    dt("debut", "Debut", "Start"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollActivityLog: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "daily_activity_log",
  tcode: "registre-daily-activity-logs",
  icon: Icons.ClipboardList,
  titre: "Journaux d' activite",
  titreEn: "Daily activity logs",
  description: "Declaration quotidienne de l' activite realisee.",
  descriptionEn: "Daily declaration of the activity performed.",
  aide: "Le contenu et la duree tracent la journee.",
  aideEn: "Content and duration trace the day.",
  lister: (params) => api.lister("coll-daily-activity-logs", params),
  creer: (data) => api.creer("coll-daily-activity-logs", data),
  modifier: (id, data) => api.modifier("coll-daily-activity-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("date", "Date", "Date"),
    col("heures", "Heures", "Hours"),
    col("activite", "Activite", "Activity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    dt("date", "Date", "Date"),
    num("heures", "Heures", "Hours"),
    txt("activite", "Activite", "Activity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollDeliverable: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "deliverable_submission",
  tcode: "registre-deliverable-submissions",
  icon: Icons.Package,
  titre: "Remises de livrables",
  titreEn: "Deliverable submissions",
  description: "Soumission d' un livrable attendu par le donneur d' ordre.",
  descriptionEn: "Submission of a deliverable expected by the client.",
  aide: "L' acceptance du livrable clot la tache.",
  aideEn: "Deliverable acceptance closes the task.",
  lister: (params) => api.lister("coll-deliverable-submissions", params),
  creer: (data) => api.creer("coll-deliverable-submissions", data),
  modifier: (id, data) => api.modifier("coll-deliverable-submissions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("livrable", "Livrable", "Deliverable"),
    col("mission", "Mission", "Mission"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("livrable", "Livrable", "Deliverable"),
    txt("mission", "Mission", "Mission"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollTimesheet: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "timesheet_declaration",
  tcode: "registre-timesheet-declarations",
  icon: Icons.Clock,
  titre: "Declarations de temps",
  titreEn: "Timesheet declarations",
  description: "Declaration du temps passe sur une mission.",
  descriptionEn: "Declaration of time spent on a mission.",
  aide: "Le cumul hebdo engage la facturation au client.",
  aideEn: "The weekly total commits the client billing.",
  lister: (params) => api.lister("coll-timesheet-declarations", params),
  creer: (data) => api.creer("coll-timesheet-declarations", data),
  modifier: (id, data) => api.modifier("coll-timesheet-declarations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("mission", "Mission", "Mission"),
    col("heures", "Heures", "Hours"),
    col("semaine", "Semaine", "Week"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("mission", "Mission", "Mission"),
    num("heures", "Heures", "Hours"),
    txt("semaine", "Semaine", "Week"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollSiteAccessLog: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "site_access_log",
  tcode: "registre-site-access-logs",
  icon: Icons.KeyRound,
  titre: "Journaux d' acces site",
  titreEn: "Site access logs",
  description: "Enregistrement d' un acces physique du collaborateur sur un site.",
  descriptionEn: "Record of a collaborator's physical access to a site.",
  aide: "L' entree / sortie atteste la presence.",
  aideEn: "Entry/exit evidences presence.",
  lister: (params) => api.lister("coll-site-access-logs", params),
  creer: (data) => api.creer("coll-site-access-logs", data),
  modifier: (id, data) => api.modifier("coll-site-access-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("site", "Site", "Site"),
    col("entree", "Entree", "Entry"),
    col("sortie", "Sortie", "Exit"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("site", "Site", "Site"),
    dtx("entree", "Entree", "Entry"),
    dtx("sortie", "Sortie", "Exit"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollWorkInstructionReceipt: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "work_instruction_receipt",
  tcode: "registre-work-instruction-receipts",
  icon: Icons.FileCheck2,
  titre: "Accuses de consignes",
  titreEn: "Work instruction receipts",
  description: "Accuse de reception d' une consigne de travail.",
  descriptionEn: "Acknowledgement of receipt of a work instruction.",
  aide: "L' accuse prouve la prise de connaissance de la consigne.",
  aideEn: "The acknowledgement evidences the instruction was read.",
  lister: (params) => api.lister("coll-work-instruction-receipts", params),
  creer: (data) => api.creer("coll-work-instruction-receipts", data),
  modifier: (id, data) => api.modifier("coll-work-instruction-receipts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("consigne", "Consigne", "Instruction"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("consigne", "Consigne", "Instruction"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollIncidentReport: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "incident_report",
  tcode: "registre-incident-reports",
  icon: Icons.AlertTriangle,
  titre: "Signalements d' incident",
  titreEn: "Incident reports",
  description: "Incident constate par le collaborateur sur le terrain.",
  descriptionEn: "Incident observed by the collaborator on the ground.",
  aide: "La date et la gravite qualifient l' incident.",
  aideEn: "Date and severity qualify the incident.",
  lister: (params) => api.lister("coll-incident-reports", params),
  creer: (data) => api.creer("coll-incident-reports", data),
  modifier: (id, data) => api.modifier("coll-incident-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("lieu", "Lieu", "Location"),
    col("description", "Description", "Description"),
    col("gravite", "Gravite", "Severity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("lieu", "Lieu", "Location"),
    txt("description", "Description", "Description"),
    txt("gravite", "Gravite", "Severity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollQualityCheck: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "quality_check_submission",
  tcode: "registre-quality-check-submissions",
  icon: Icons.CheckCircle2,
  titre: "Remises de controles qualite",
  titreEn: "Quality check submissions",
  description: "Resultat d' un controle qualite saisi par le collaborateur.",
  descriptionEn: "Result of a quality check entered by the collaborator.",
  aide: "La conformite mesuree conditionne la validation.",
  aideEn: "The measured conformity conditions validation.",
  lister: (params) => api.lister("coll-quality-check-submissions", params),
  creer: (data) => api.creer("coll-quality-check-submissions", data),
  modifier: (id, data) => api.modifier("coll-quality-check-submissions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("controle", "Controle", "Check"),
    col("point_testes", "Points testes", "Points tested"),
    col("anomalies", "Anomalies", "Defects"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("controle", "Controle", "Check"),
    num("point_testes", "Points testes", "Points tested"),
    num("anomalies", "Anomalies", "Defects"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollTrainingCompletion: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "training_completion",
  tcode: "registre-training-completions",
  icon: Icons.GraduationCap,
  titre: "Attestations de formation",
  titreEn: "Training completions",
  description: "Validation de la fin d' une formation par le collaborateur.",
  descriptionEn: "Validation of the end of a training by the collaborator.",
  aide: "Le succes conditionne l' habilitation delivree.",
  aideEn: "Success conditions the issued authorization.",
  lister: (params) => api.lister("coll-training-completions", params),
  creer: (data) => api.creer("coll-training-completions", data),
  modifier: (id, data) => api.modifier("coll-training-completions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("formation", "Formation", "Training"),
    col("date", "Date", "Date"),
    col("score", "Score", "Score"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("formation", "Formation", "Training"),
    dt("date", "Date", "Date"),
    num("score", "Score", "Score"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollEquipmentIssue: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "equipment_issue",
  tcode: "registre-equipment-issues",
  icon: Icons.Wrench,
  titre: "Signalements de probleme equipement",
  titreEn: "Equipment issues",
  description: "Probleme rencontre sur un equipement mis a disposition.",
  descriptionEn: "Problem met on a provided equipment.",
  aide: "Le blocage d' un equipement immobilise la tache.",
  aideEn: "A blocked equipment halts the task.",
  lister: (params) => api.lister("coll-equipment-issues", params),
  creer: (data) => api.creer("coll-equipment-issues", data),
  modifier: (id, data) => api.modifier("coll-equipment-issues", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("equipement", "Equipement", "Equipment"),
    col("probleme", "Probleme", "Problem"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("equipement", "Equipement", "Equipment"),
    txt("probleme", "Probleme", "Problem"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollShiftAttendance: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "shift_attendance",
  tcode: "registre-shift-attendance",
  icon: Icons.CalendarCheck,
  titre: "Presences par poste",
  titreEn: "Shift attendance",
  description: "Enregistrement de presence sur un poste de travail.",
  descriptionEn: "Attendance record on a work shift.",
  aide: "La presence effective conditionne la paie.",
  aideEn: "Actual attendance conditions the payroll.",
  lister: (params) => api.lister("coll-shift-attendance", params),
  creer: (data) => api.creer("coll-shift-attendance", data),
  modifier: (id, data) => api.modifier("coll-shift-attendance", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("poste", "Poste", "Shift"),
    col("date", "Date", "Date"),
    col("arrivee", "Arrivee", "Arrival"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("poste", "Poste", "Shift"),
    dt("date", "Date", "Date"),
    dtx("arrivee", "Arrivee", "Arrival"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollTravelOrder: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "travel_order",
  tcode: "registre-travel-orders",
  icon: Icons.Navigation,
  titre: "Ordres de mission",
  titreEn: "Travel orders",
  description: "Ordre de mission autorisant un deplacement.",
  descriptionEn: "Travel order authorizing a trip.",
  aide: "Le trajet autorise et la duree encadrent la mission.",
  aideEn: "The authorized route and duration bound the mission.",
  lister: (params) => api.lister("coll-travel-orders", params),
  creer: (data) => api.creer("coll-travel-orders", data),
  modifier: (id, data) => api.modifier("coll-travel-orders", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("destination", "Destination", "Destination"),
    col("debut", "Debut", "Start"),
    col("fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("destination", "Destination", "Destination"),
    dt("debut", "Debut", "Start"),
    dt("fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollExpenseDeclaration: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "expense_declaration",
  tcode: "registre-expense-declarations",
  icon: Icons.Receipt,
  titre: "Declarations de frais",
  titreEn: "Expense declarations",
  description: "Declaration de frais engages en mission par le collaborateur.",
  descriptionEn: "Declaration of expenses incurred on mission.",
  aide: "Le montant doit etre appuye par des justificatifs.",
  aideEn: "The amount must be backed by receipts.",
  lister: (params) => api.lister("coll-expense-declarations", params),
  creer: (data) => api.creer("coll-expense-declarations", data),
  modifier: (id, data) => api.modifier("coll-expense-declarations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("mission", "Mission", "Mission"),
    col("montant", "Montant", "Amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("mission", "Mission", "Mission"),
    num("montant", "Montant", "Amount"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollCertificationUpload: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "certification_upload",
  tcode: "registre-certification-uploads",
  icon: Icons.FileBadge,
  titre: "Depot de certifications",
  titreEn: "Certification uploads",
  description: "Depot par le collaborateur d' une piece de certification.",
  descriptionEn: "Collaborator upload of a certification document.",
  aide: "La validite de la piece maintient l' habilitation active.",
  aideEn: "Document validity keeps the authorization active.",
  lister: (params) => api.lister("coll-certification-uploads", params),
  creer: (data) => api.creer("coll-certification-uploads", data),
  modifier: (id, data) => api.modifier("coll-certification-uploads", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("certification", "Certification", "Certification"),
    col("expire_le", "Expire le", "Expires"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("certification", "Certification", "Certification"),
    dt("expire_le", "Expire le", "Expires"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollTaskCompletion: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "task_completion",
  tcode: "registre-task-completions",
  icon: Icons.CheckCircle2,
  titre: "Achevements de taches",
  titreEn: "Task completions",
  description: "Cloture d' une tache assignee au collaborateur.",
  descriptionEn: "Closure of a task assigned to the collaborator.",
  aide: "L' horodatage d' achevement alimente le suivi de charge.",
  aideEn: "The completion timestamp feeds workload tracking.",
  lister: (params) => api.lister("coll-task-completions", params),
  creer: (data) => api.creer("coll-task-completions", data),
  modifier: (id, data) => api.modifier("coll-task-completions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("tache", "Tache", "Task"),
    col("acheve_le", "Acheve le", "Completed at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("tache", "Tache", "Task"),
    dtx("acheve_le", "Acheve le", "Completed at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollFeedback: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "feedback_submission",
  tcode: "registre-feedback-submissions",
  icon: Icons.Send,
  titre: "Remontees terrain",
  titreEn: "Feedback submissions",
  description: "Retour d' experience emis par le collaborateur sur le terrain.",
  descriptionEn: "Field feedback raised by the collaborator.",
  aide: "La remontee alimente l' amelioration continue.",
  aideEn: "The feedback feeds continuous improvement.",
  lister: (params) => api.lister("coll-feedback-submissions", params),
  creer: (data) => api.creer("coll-feedback-submissions", data),
  modifier: (id, data) => api.modifier("coll-feedback-submissions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("sujet", "Sujet", "Topic"),
    col("contenu", "Contenu", "Content"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("sujet", "Sujet", "Topic"),
    txt("contenu", "Contenu", "Content"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollAvailability: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "availability_declaration",
  tcode: "registre-availability-declarations",
  icon: Icons.CalendarClock,
  titre: "Declarations de disponibilite",
  titreEn: "Availability declarations",
  description: "Disponible declaree par le collaborateur pour une periode.",
  descriptionEn: "Availability declared by the collaborator for a period.",
  aide: "La disponibilite conditionne l' affectation future.",
  aideEn: "Availability conditions future assignment.",
  lister: (params) => api.lister("coll-availability-declarations", params),
  creer: (data) => api.creer("coll-availability-declarations", data),
  modifier: (id, data) => api.modifier("coll-availability-declarations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("periode", "Periode", "Period"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("periode", "Periode", "Period"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollContractRenewalRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "contract_renewal_request",
  tcode: "registre-contract-renewal-requests",
  icon: Icons.FileSignature,
  titre: "Demandes de renouvellement de contrat",
  titreEn: "Contract renewal requests",
  description: "Demande de renouvellement du contrat du collaborateur.",
  descriptionEn: "Request to renew the collaborator's contract.",
  aide: "L' echeance contractuelle impose l' anticipation.",
  aideEn: "The contract end date forces anticipation.",
  lister: (params) => api.lister("coll-contract-renewal-requests", params),
  creer: (data) => api.creer("coll-contract-renewal-requests", data),
  modifier: (id, data) => api.modifier("coll-contract-renewal-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("echeance", "Echeance", "End date"),
    col("type", "Type", "Type"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    dt("echeance", "Echeance", "End date"),
    txt("type", "Type", "Type"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCollDocumentRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "document_request",
  tcode: "registre-document-requests",
  icon: Icons.FolderSearch,
  titre: "Demandes de documents",
  titreEn: "Document requests",
  description: "Demande d' un document administratif au collaborateur.",
  descriptionEn: "Request for an administrative document from the collaborator.",
  aide: "La reponse dans les delais conditionne la conformite du dossier.",
  aideEn: "Timely response conditions file compliance.",
  lister: (params) => api.lister("coll-document-requests", params),
  creer: (data) => api.creer("coll-document-requests", data),
  modifier: (id, data) => api.modifier("coll-document-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Collaborator"),
    col("document", "Document", "Document"),
    col("delai", "Delai", "Deadline"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Collaborator"),
    txt("document", "Document", "Document"),
    dt("delai", "Delai", "Deadline"),
    txt("statut", "Statut", "Status"),
  ],
};

