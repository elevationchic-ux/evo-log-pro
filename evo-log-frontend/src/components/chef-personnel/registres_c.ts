/**
 * Configs Registre pour chef-personnel (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("chef-personnel");

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

export const registreChpRecruitmentCampaign: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "recruitment_campaign",
  tcode: "registre-recruitment-campaigns",
  icon: Icons.Users,
  titre: "Campagnes de recrutement",
  titreEn: "Recruitment campaigns",
  description: "Ouverture d' une campagne de recrutement pour un besoin.",
  descriptionEn: "Opening of a recruitment campaign for a need.",
  aide: "Le poste et le volume attendu cadrent la campagne.",
  aideEn: "The role and expected volume frame the campaign.",
  lister: (params) => api.lister("chp-recruitment-campaigns", params),
  creer: (data) => api.creer("chp-recruitment-campaigns", data),
  modifier: (id, data) => api.modifier("chp-recruitment-campaigns", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("poste", "Poste", "Role"),
    col("volume", "Volume", "Volume"),
    col("ouverture", "Ouverture", "Opening"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("poste", "Poste", "Role"),
    num("volume", "Volume", "Volume"),
    dt("ouverture", "Ouverture", "Opening"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpJobPosting: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "job_posting",
  tcode: "registre-job-postings",
  icon: Icons.Briefcase,
  titre: "Offres d' emploi",
  titreEn: "Job postings",
  description: "Publication d' une offre pour un poste a pourvoir.",
  descriptionEn: "Publication of a job offer for an open role.",
  aide: "Le canal et la date de parution pilotent l' audience.",
  aideEn: "Channel and publish date drive reach.",
  lister: (params) => api.lister("chp-job-postings", params),
  creer: (data) => api.creer("chp-job-postings", data),
  modifier: (id, data) => api.modifier("chp-job-postings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("intitule", "Intitule", "Title"),
    col("canal", "Canal", "Channel"),
    col("parution", "Parution", "Published"),
    col("candidats", "Candidats", "Candidates"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("intitule", "Intitule", "Title"),
    txt("canal", "Canal", "Channel"),
    dt("parution", "Parution", "Published"),
    num("candidats", "Candidats", "Candidates"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpCandidateSelection: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "candidate_selection",
  tcode: "registre-candidate-selections",
  icon: Icons.ListChecks,
  titre: "Selection de candidats",
  titreEn: "Candidate selections",
  description: "Decision de selection sur un candidat a un poste.",
  descriptionEn: "Selection decision on a candidate for a role.",
  aide: "La phase du tunnel trace l' avancement.",
  aideEn: "The pipeline stage traces the progress.",
  lister: (params) => api.lister("chp-candidate-selections", params),
  creer: (data) => api.creer("chp-candidate-selections", data),
  modifier: (id, data) => api.modifier("chp-candidate-selections", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("candidat", "Candidat", "Candidate"),
    col("poste", "Poste", "Role"),
    col("phase", "Phase", "Stage"),
    col("evaluateur", "Evaluateur", "Evaluator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("candidat", "Candidat", "Candidate"),
    txt("poste", "Poste", "Role"),
    txt("phase", "Phase", "Stage"),
    txt("evaluateur", "Evaluateur", "Evaluator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpInterviewSchedule: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "interview_schedule",
  tcode: "registre-interview-schedules",
  icon: Icons.CalendarDays,
  titre: "Planifications d' entretiens",
  titreEn: "Interview schedules",
  description: "Creneau d' entretien fixe entre un candidat et un evaluateur.",
  descriptionEn: "Interview slot between a candidate and an evaluator.",
  aide: "Le format et les participants conditionnent l' entretien.",
  aideEn: "Format and participants condition the interview.",
  lister: (params) => api.lister("chp-interview-schedules", params),
  creer: (data) => api.creer("chp-interview-schedules", data),
  modifier: (id, data) => api.modifier("chp-interview-schedules", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("candidat", "Candidat", "Candidate"),
    col("date", "Date", "Date"),
    col("format", "Format", "Format"),
    col("evaluateur", "Evaluateur", "Evaluator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("candidat", "Candidat", "Candidate"),
    dtx("date", "Date", "Date"),
    txt("format", "Format", "Format"),
    txt("evaluateur", "Evaluateur", "Evaluator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpOfferApproval: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "offer_approval",
  tcode: "registre-offer-approvals",
  icon: Icons.FileCheck2,
  titre: "Validations d' offres",
  titreEn: "Offer approvals",
  description: "Circuit de validation d' une proposition d' embauche.",
  descriptionEn: "Approval workflow of a hiring offer.",
  aide: "La remuneration proposee doit respecter la fourchette budgetaire.",
  aideEn: "The proposed pay must respect the budget range.",
  lister: (params) => api.lister("chp-offer-approvals", params),
  creer: (data) => api.creer("chp-offer-approvals", data),
  modifier: (id, data) => api.modifier("chp-offer-approvals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("candidat", "Candidat", "Candidate"),
    col("poste", "Poste", "Role"),
    col("remuneration", "Remuneration", "Compensation"),
    col("validateur", "Validateur", "Approver"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("candidat", "Candidat", "Candidate"),
    txt("poste", "Poste", "Role"),
    num("remuneration", "Remuneration", "Compensation"),
    txt("validateur", "Validateur", "Approver"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpOnboardingChecklist: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "onboarding_checklist",
  tcode: "registre-onboarding-checklists",
  icon: Icons.ClipboardList,
  titre: "Checklists d' integration",
  titreEn: "Onboarding checklists",
  description: "Jalons d' integration d' un nouveau arrive.",
  descriptionEn: "Onboarding milestones of a new hire.",
  aide: "Le taux d' etapes faites mesure la qualite de l' arrivee.",
  aideEn: "The completion rate measures arrival quality.",
  lister: (params) => api.lister("chp-onboarding-checklists", params),
  creer: (data) => api.creer("chp-onboarding-checklists", data),
  modifier: (id, data) => api.modifier("chp-onboarding-checklists", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("etapes_total", "Etapes", "Steps"),
    col("etapes_faites", "Etapes faites", "Steps done"),
    col("date_debut", "Debut", "Start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    num("etapes_total", "Etapes", "Steps"),
    num("etapes_faites", "Etapes faites", "Steps done"),
    dt("date_debut", "Debut", "Start"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpProbationReview: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "probation_review",
  tcode: "registre-probation-reviews",
  icon: Icons.FileSignature,
  titre: "Revues de periode d' essai",
  titreEn: "Probation reviews",
  description: "Bilan de fin de periode d' essai d' un collaborateur.",
  descriptionEn: "End-of-probation assessment of an employee.",
  aide: "La decision (titulariser / renouveler) clot l' essai.",
  aideEn: "The decision (confirm/renew) closes the trial.",
  lister: (params) => api.lister("chp-probation-reviews", params),
  creer: (data) => api.creer("chp-probation-reviews", data),
  modifier: (id, data) => api.modifier("chp-probation-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("date_echeance", "Echeance", "Due date"),
    col("avis", "Avis", "Verdict"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    dt("date_echeance", "Echeance", "Due date"),
    txt("avis", "Avis", "Verdict"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpExitInterview: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "exit_interview",
  tcode: "registre-exit-interviews",
  icon: Icons.BookOpen,
  titre: "Entretiens de depart",
  titreEn: "Exit interviews",
  description: "Entretien realise lors du depart d' un collaborateur.",
  descriptionEn: "Interview conducted on an employee's departure.",
  aide: "La motif de depart alimente la marque employeur.",
  aideEn: "The departure reason feeds employer brand.",
  lister: (params) => api.lister("chp-exit-interviews", params),
  creer: (data) => api.creer("chp-exit-interviews", data),
  modifier: (id, data) => api.modifier("chp-exit-interviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("motif", "Motif", "Reason"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("motif", "Motif", "Reason"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpHeadcountRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "headcount_request",
  tcode: "registre-headcount-requests",
  icon: Icons.TrendingUp,
  titre: "Demandes de creation de poste",
  titreEn: "Headcount requests",
  description: "Demande de validation d' un nouveau poste.",
  descriptionEn: "Request to validate a new position.",
  aide: "Le budget et la justification encadrent la demande.",
  aideEn: "Budget and justification frame the request.",
  lister: (params) => api.lister("chp-headcount-requests", params),
  creer: (data) => api.creer("chp-headcount-requests", data),
  modifier: (id, data) => api.modifier("chp-headcount-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("departement", "Departement", "Department"),
    col("poste", "Poste", "Role"),
    col("masse_salariale", "Masse salariale", "Salary cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("departement", "Departement", "Department"),
    txt("poste", "Poste", "Role"),
    num("masse_salariale", "Masse salariale", "Salary cost"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpOrgMovement: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "org_movement",
  tcode: "registre-org-movements",
  icon: Icons.GitBranch,
  titre: "Mouvements organisationnels",
  titreEn: "Org movements",
  description: "Changement de service, manager ou niveau d' un collaborateur.",
  descriptionEn: "Change of department, manager or level for an employee.",
  aide: "La date d' effet redecrit l' organigramme.",
  aideEn: "The effective date rewrites the org chart.",
  lister: (params) => api.lister("chp-org-movements", params),
  creer: (data) => api.creer("chp-org-movements", data),
  modifier: (id, data) => api.modifier("chp-org-movements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("type_mouvement", "Type", "Movement type"),
    col("date_effet", "Date d' effet", "Effective date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("type_mouvement", "Type", "Movement type"),
    dt("date_effet", "Date d' effet", "Effective date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpDisciplinaryAction: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "disciplinary_action",
  tcode: "registre-disciplinary-actions",
  icon: Icons.AlertTriangle,
  titre: "Mesures disciplinaires",
  titreEn: "Disciplinary actions",
  description: "Sanction ou mesure disciplinaire decidee a l' encontre d' un collaborateur.",
  descriptionEn: "Sanction or disciplinary measure decided against an employee.",
  aide: "La gravite et la procedure garantie tracent la mesure.",
  aideEn: "Severity and due process trace the measure.",
  lister: (params) => api.lister("chp-disciplinary-actions", params),
  creer: (data) => api.creer("chp-disciplinary-actions", data),
  modifier: (id, data) => api.modifier("chp-disciplinary-actions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("motif", "Motif", "Reason"),
    col("type_mesure", "Type de mesure", "Measure type"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("motif", "Motif", "Reason"),
    txt("type_mesure", "Type de mesure", "Measure type"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpTrainingPlan: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "training_plan",
  tcode: "registre-training-plans",
  icon: Icons.Target,
  titre: "Plans de formation",
  titreEn: "Training plans",
  description: "Plan de formation annuel arbitre pour un departement.",
  descriptionEn: "Annual training plan arbitrated for a department.",
  aide: "Le budget et les priorites cadrent le plan.",
  aideEn: "Budget and priorities frame the plan.",
  lister: (params) => api.lister("chp-training-plans", params),
  creer: (data) => api.creer("chp-training-plans", data),
  modifier: (id, data) => api.modifier("chp-training-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("departement", "Departement", "Department"),
    col("exercice", "Exercice", "Fiscal year"),
    col("budget", "Budget", "Budget"),
    col("actions", "Actions", "Actions"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("departement", "Departement", "Department"),
    txt("exercice", "Exercice", "Fiscal year"),
    num("budget", "Budget", "Budget"),
    num("actions", "Actions", "Actions"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpAbsenceApproval: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "absence_approval",
  tcode: "registre-absence-approvals",
  icon: Icons.CalendarCheck,
  titre: "Validations d' absences",
  titreEn: "Absence approvals",
  description: "Validation manager d' une demande d' absence d' un collaborateur.",
  descriptionEn: "Manager approval of an employee's absence request.",
  aide: "Le solde et la charge d' equipe conditionnent l' accord.",
  aideEn: "Balance and team load condition the approval.",
  lister: (params) => api.lister("chp-absence-approvals", params),
  creer: (data) => api.creer("chp-absence-approvals", data),
  modifier: (id, data) => api.modifier("chp-absence-approvals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("manager", "Manager", "Manager"),
    col("debut", "Debut", "Start"),
    col("fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("manager", "Manager", "Manager"),
    dt("debut", "Debut", "Start"),
    dt("fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpPayrollAdjustmentRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "payroll_adjustment_request",
  tcode: "registre-payroll-adjustment-requests",
  icon: Icons.Banknote,
  titre: "Demandes d' ajustement de paie",
  titreEn: "Payroll adjustment requests",
  description: "Demande d' ajustement exceptionnel de la paie d' un collaborateur.",
  descriptionEn: "Exceptional payroll adjustment request for an employee.",
  aide: "Le montant et la justification engagent le controle RH.",
  aideEn: "The amount and justification commit the HR control.",
  lister: (params) => api.lister("chp-payroll-adjustment-requests", params),
  creer: (data) => api.creer("chp-payroll-adjustment-requests", data),
  modifier: (id, data) => api.modifier("chp-payroll-adjustment-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("motif", "Motif", "Reason"),
    col("montant", "Montant", "Amount"),
    col("periode", "Periode", "Period"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("motif", "Motif", "Reason"),
    num("montant", "Montant", "Amount"),
    txt("periode", "Periode", "Period"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreChpPolicyAck: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "policy_ack",
  tcode: "registre-policy-acknowledgements",
  icon: Icons.FileText,
  titre: "Accuses de politique RH",
  titreEn: "Policy acknowledgements",
  description: "Prise de connaissance et acceptation d' une politique RH.",
  descriptionEn: "Reading and acceptance of an HR policy.",
  aide: "L' accuse horodate prouve la diffusion de la regle.",
  aideEn: "The timestamped acknowledgement proves rule dissemination.",
  lister: (params) => api.lister("chp-policy-acknowledgements", params),
  creer: (data) => api.creer("chp-policy-acknowledgements", data),
  modifier: (id, data) => api.modifier("chp-policy-acknowledgements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("politique", "Politique", "Policy"),
    col("version", "Version", "Version"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("politique", "Politique", "Policy"),
    txt("version", "Version", "Version"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

