/**
 * Configs Registre pour rh-personnel (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("rh-personnel");

function col(key: string, header: string, headerEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {
  return { key, header, headerEn, ...opts } as ColonneRegistre;
}

function txt(key: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { key, label, labelEn, type: "text", ...opts } as ChampRegistre;
}

function num(key: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {
  return { key, label, labelEn, type: "number", ...opts } as ChampRegistre;
}

function dt(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "date" } as ChampRegistre;
}

function dtx(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "datetime-local" } as ChampRegistre;
}

function area(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "textarea" } as ChampRegistre;
}

function chk(key: string, label: string, labelEn: string): ChampRegistre {
  return { key, label, labelEn, type: "checkbox" } as ChampRegistre;
}

function sel(key: string, label: string, labelEn: string, nomKey: string): ChampRegistre {
  return { key, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;
}

function filtreSel(key: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {
  return { key, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;
}

export const registreRecruitment: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "recruitment",
  tcode: "registre-recruitment",
  icon: Icons.UserPlus,
  titre: "Offres et candidatures",
  titreEn: "Job offers and applications",
  description: "Pipeline de recrutement par poste.",
  descriptionEn: "Recruitment pipeline by position.",
  aide: "Avis obligatoire pour chaque candidat.",
  aideEn: "Feedback mandatory per candidate.",
  lister: (params) => api.lister("recruitments", params),
  creer: (data) => api.creer("recruitments", data),
  modifier: (id, data) => api.modifier("recruitments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("poste", "Poste", "Position"),
    col("departement", "Departement", "Department"),
    col("type_contrat", "Type contrat", "Contract type"),
    col("date_ouverture", "Ouverture", "Opening"),
    col("date_cloture", "Cloture", "Closing"),
    col("candidats_recus", "Candidats", "Candidates"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("poste", "Poste", "Position"),
    txt("departement", "Departement", "Department"),
    sel("type_contrat", "Type contrat", "Contract type", "type_contrat"),
    dt("date_ouverture", "Ouverture", "Opening"),
    dt("date_cloture", "Cloture", "Closing"),
    num("candidats_recus", "Candidats", "Candidates"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreTrainingPlan: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "training",
  tcode: "registre-training",
  icon: Icons.GraduationCap,
  titre: "Plan de formation",
  titreEn: "Training plan",
  description: "Actions de formation et habilitations.",
  descriptionEn: "Training and qualification actions.",
  aide: "Habilitation obligatoire avant prise de poste.",
  aideEn: "Qualification required before role.",
  lister: (params) => api.lister("training-plans", params),
  creer: (data) => api.creer("training-plans", data),
  modifier: (id, data) => api.modifier("training-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("intitule", "Intitule", "Title"),
    col("type_action", "Type", "Type"),
    col("organisme", "Organisme", "Provider"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("duree_heures", "Duree (h)", "Duration (h)"),
    col("cout_xaf", "Cout", "Cost"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("intitule", "Intitule", "Title"),
    sel("type_action", "Type", "Type", "type_action"),
    txt("organisme", "Organisme", "Provider"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    num("duree_heures", "Duree (h)", "Duration (h)"),
    num("cout_xaf", "Cout", "Cost"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registrePerformanceReview: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "performance_review",
  tcode: "registre-performance-reviews",
  icon: Icons.Star,
  titre: "Entretiens d'evaluation",
  titreEn: "Performance reviews",
  description: "Evaluations periodiques des salaries.",
  descriptionEn: "Periodic employee reviews.",
  aide: "Double validation N+1 et RH.",
  aideEn: "Dual sign-off by manager and HR.",
  lister: (params) => api.lister("performance-reviews", params),
  creer: (data) => api.creer("performance-reviews", data),
  modifier: (id, data) => api.modifier("performance-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("periode", "Periode", "Period"),
    col("date_entretien", "Date entretien", "Interview date"),
    col("evaluateur", "Evaluateur", "Evaluator"),
    col("note_global", "Note globale", "Overall score"),
    col("objectifs_atteints_pct", "Objectifs atteints %", "Goals reached %"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    txt("periode", "Periode", "Period"),
    dt("date_entretien", "Date entretien", "Interview date"),
    txt("evaluateur", "Evaluateur", "Evaluator"),
    num("note_global", "Note globale", "Overall score"),
    num("objectifs_atteints_pct", "Objectifs atteints %", "Goals reached %"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreDisciplinaryCase: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "disciplinary",
  tcode: "registre-disciplinary",
  icon: Icons.Gavel,
  titre: "Procedures disciplinaires",
  titreEn: "Disciplinary procedures",
  description: "Avertissements, mises a pied, sanctions.",
  descriptionEn: "Warnings, suspensions, sanctions.",
  aide: "Respect du droit de defense.",
  aideEn: "Defense rights respected.",
  lister: (params) => api.lister("disciplinary-cases", params),
  creer: (data) => api.creer("disciplinary-cases", data),
  modifier: (id, data) => api.modifier("disciplinary-cases", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("date_fait", "Date du fait", "Incident date"),
    col("type_sanction", "Type sanction", "Sanction type"),
    col("motif", "Motif", "Reason"),
    col("date_convocation", "Convocation", "Hearing date"),
    col("date_decision", "Decision", "Decision date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    dt("date_fait", "Date du fait", "Incident date"),
    sel("type_sanction", "Type sanction", "Sanction type", "type_sanction"),
    txt("motif", "Motif", "Reason"),
    dt("date_convocation", "Convocation", "Hearing date"),
    dt("date_decision", "Decision", "Decision date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreOrgUnit: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "org_chart",
  tcode: "registre-org-chart",
  icon: Icons.Network,
  titre: "Organigramme",
  titreEn: "Org chart",
  description: "Unites hierarchiques.",
  descriptionEn: "Hierarchical units.",
  aide: "Chaque unite a un responsable.",
  aideEn: "Each unit has a lead.",
  lister: (params) => api.lister("org-units", params),
  creer: (data) => api.creer("org-units", data),
  modifier: (id, data) => api.modifier("org-units", id, data),
  unicite: "code_unite",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_unite", "Code unite", "Unit code", { searchable: true }),
    col("nom", "Nom", "Name"),
    col("parent_code", "Code parent", "Parent code"),
    col("type_unite", "Type", "Type"),
    col("responsable", "Responsable", "Lead"),
    col("effectif", "Effectif", "Headcount"),
  ],
  champs: [
    txt("code_unite", "Code unite", "Unit code", { obligatoire: true }),
    txt("nom", "Nom", "Name"),
    txt("parent_code", "Code parent", "Parent code"),
    sel("type_unite", "Type", "Type", "type_unite"),
    txt("responsable", "Responsable", "Lead"),
    num("effectif", "Effectif", "Headcount"),
  ],
};


export const registreWorkforcePlan: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "workforce_planning",
  tcode: "registre-workforce-planning",
  icon: Icons.Calculator,
  titre: "Masse salariale previsionnelle",
  titreEn: "Forecast payroll",
  description: "Projection mensuelle de masse salariale.",
  descriptionEn: "Monthly payroll projection.",
  aide: "Ajustee a chaque mouvement RH.",
  aideEn: "Adjusted on HR moves.",
  lister: (params) => api.lister("workforce-plans", params),
  creer: (data) => api.creer("workforce-plans", data),
  modifier: (id, data) => api.modifier("workforce-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("exercice", "Exercice", "Fiscal year"),
    col("mois", "Mois", "Month"),
    col("masse_salariale_prevue_xaf", "Masse prevue", "Forecast payroll"),
    col("effectif_cadre", "Cadres", "Exec headcount"),
    col("effectif_non_cadre", "Non-cadres", "Non-exec headcount"),
    col("hypothese_inflation_pct", "Inflation %", "Inflation %"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("exercice", "Exercice", "Fiscal year"),
    txt("mois", "Mois", "Month"),
    num("masse_salariale_prevue_xaf", "Masse prevue", "Forecast payroll"),
    num("effectif_cadre", "Cadres", "Exec headcount"),
    num("effectif_non_cadre", "Non-cadres", "Non-exec headcount"),
    num("hypothese_inflation_pct", "Inflation %", "Inflation %"),
  ],
};


export const registreEmploymentContract: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "contract_management",
  tcode: "registre-contract-management",
  icon: Icons.FileSignature,
  titre: "Suivi contrats",
  titreEn: "Contract tracking",
  description: "Contrats de travail avec renouvellements.",
  descriptionEn: "Employment contracts and renewals.",
  aide: "Alerte avant expiration CDD.",
  aideEn: "Alert before fixed-term expiry.",
  lister: (params) => api.lister("employment-contracts", params),
  creer: (data) => api.creer("employment-contracts", data),
  modifier: (id, data) => api.modifier("employment-contracts", id, data),
  unicite: "numero_contrat",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_contrat", "Numero contrat", "Contract number", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("type_contrat", "Type contrat", "Contract type"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("avenants", "Avenants", "Amendments"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_contrat", "Numero contrat", "Contract number", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    sel("type_contrat", "Type contrat", "Contract type", "type_contrat"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    txt("avenants", "Avenants", "Amendments"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreEmployeeBenefit: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "benefits",
  tcode: "registre-benefits",
  icon: Icons.Gift,
  titre: "Avantages",
  titreEn: "Benefits",
  description: "Mutuelle, transport, logement.",
  descriptionEn: "Health, transport, housing.",
  aide: "Plafond annuel par categorie.",
  aideEn: "Annual ceiling per category.",
  lister: (params) => api.lister("employee-benefits", params),
  creer: (data) => api.creer("employee-benefits", data),
  modifier: (id, data) => api.modifier("employee-benefits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("type_avantage", "Type avantage", "Benefit type"),
    col("montant_annuel_xaf", "Montant annuel", "Annual amount"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    sel("type_avantage", "Type avantage", "Benefit type", "type_avantage"),
    num("montant_annuel_xaf", "Montant annuel", "Annual amount"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreEmployeeExit: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "exit_management",
  tcode: "registre-exit-management",
  icon: Icons.DoorClosed,
  titre: "Depart / solde tout compte",
  titreEn: "Exit / final settlement",
  description: "Dossiers de sortie.",
  descriptionEn: "Departure files.",
  aide: "Recapitulatif obligatoire.",
  aideEn: "Mandatory recap.",
  lister: (params) => api.lister("employee-exits", params),
  creer: (data) => api.creer("employee-exits", data),
  modifier: (id, data) => api.modifier("employee-exits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("type_depart", "Type depart", "Exit type"),
    col("date_depart", "Date depart", "Exit date"),
    col("preavis_debut", "Preavis debut", "Notice start"),
    col("preavis_fin", "Preavis fin", "Notice end"),
    col("solde_tout_compte_xaf", "Solde tout compte", "Final settlement"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    sel("type_depart", "Type depart", "Exit type", "type_depart"),
    dt("date_depart", "Date depart", "Exit date"),
    dt("preavis_debut", "Preavis debut", "Notice start"),
    dt("preavis_fin", "Preavis fin", "Notice end"),
    num("solde_tout_compte_xaf", "Solde tout compte", "Final settlement"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreAttendanceDevice: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "attendance_device",
  tcode: "registre-attendance-devices",
  icon: Icons.ScanFace,
  titre: "Pointage / badgeuses",
  titreEn: "Attendance devices",
  description: "Terminaux de badgeage.",
  descriptionEn: "Badge terminals.",
  aide: "Sync quotidienne.",
  aideEn: "Daily sync.",
  lister: (params) => api.lister("attendance-devices", params),
  creer: (data) => api.creer("attendance-devices", data),
  modifier: (id, data) => api.modifier("attendance-devices", id, data),
  unicite: "code_terminal",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_terminal", "Code terminal", "Terminal code", { searchable: true }),
    col("lieu", "Lieu", "Location"),
    col("type_terminal", "Type", "Type"),
    col("adresse_ip", "Adresse IP", "IP address"),
    col("derniere_synchro", "Derniere sync", "Last sync"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_terminal", "Code terminal", "Terminal code", { obligatoire: true }),
    txt("lieu", "Lieu", "Location"),
    sel("type_terminal", "Type", "Type", "type_terminal"),
    txt("adresse_ip", "Adresse IP", "IP address"),
    dtx("derniere_synchro", "Derniere sync", "Last sync"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreLeaveQuota: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "leave_quota",
  tcode: "registre-leave-quotas",
  icon: Icons.Calendar,
  titre: "Droits conges / report N-1",
  titreEn: "Leave entitlements / carry-over",
  description: "Solde conges payes.",
  descriptionEn: "Paid leave balance.",
  aide: "Report plafonne.",
  aideEn: "Capped carry-over.",
  lister: (params) => api.lister("leave-quotas", params),
  creer: (data) => api.creer("leave-quotas", data),
  modifier: (id, data) => api.modifier("leave-quotas", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("exercice", "Exercice", "Fiscal year"),
    col("droit_initial_jours", "Droit initial (j)", "Initial entitlement (d)"),
    col("jours_pris", "Jours pris", "Days taken"),
    col("jours_reportes", "Jours reportes", "Days carried"),
    col("solde_actuel", "Solde actuel", "Current balance"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    num("exercice", "Exercice", "Fiscal year"),
    num("droit_initial_jours", "Droit initial (j)", "Initial entitlement (d)"),
    num("jours_pris", "Jours pris", "Days taken"),
    num("jours_reportes", "Jours reportes", "Days carried"),
    num("solde_actuel", "Solde actuel", "Current balance"),
  ],
};


export const registreEmployeeSkill: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "skills_matrix",
  tcode: "registre-skills-matrix",
  icon: Icons.Grid3x3,
  titre: "Matrice de competences",
  titreEn: "Skills matrix",
  description: "Competences par employe.",
  descriptionEn: "Skills per employee.",
  aide: "Maj annuelle RH.",
  aideEn: "Annual HR update.",
  lister: (params) => api.lister("employee-skills", params),
  creer: (data) => api.creer("employee-skills", data),
  modifier: (id, data) => api.modifier("employee-skills", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("competence", "Competence", "Skill"),
    col("niveau", "Niveau", "Level"),
    col("date_evaluation", "Date evaluation", "Assessment date"),
    col("date_expiration", "Expiration", "Expiry"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    txt("competence", "Competence", "Skill"),
    sel("niveau", "Niveau", "Level", "niveau"),
    dt("date_evaluation", "Date evaluation", "Assessment date"),
    dt("date_expiration", "Expiration", "Expiry"),
  ],
};


export const registreHrReport: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "hr_reports",
  tcode: "registre-hr-reports",
  icon: Icons.FileBarChart,
  titre: "Rapports RH periodiques",
  titreEn: "Periodic HR reports",
  description: "Effectif, absent., turnover.",
  descriptionEn: "Headcount, absence, turnover.",
  aide: "Diffusion mensuelle direction.",
  aideEn: "Monthly leadership distribution.",
  lister: (params) => api.lister("hr-reports", params),
  creer: (data) => api.creer("hr-reports", data),
  modifier: (id, data) => api.modifier("hr-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("periode_debut", "Debut", "Start"),
    col("periode_fin", "Fin", "End"),
    col("effectif_debut", "Effectif debut", "Opening headcount"),
    col("effectif_fin", "Effectif fin", "Closing headcount"),
    col("taux_absent_pct", "Absent. %", "Absence %"),
    col("taux_turnover_pct", "Turnover %", "Turnover %"),
    col("masse_salariale_xaf", "Masse salariale", "Payroll"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    dt("periode_debut", "Debut", "Start"),
    dt("periode_fin", "Fin", "End"),
    num("effectif_debut", "Effectif debut", "Opening headcount"),
    num("effectif_fin", "Effectif fin", "Closing headcount"),
    num("taux_absent_pct", "Absent. %", "Absence %"),
    num("taux_turnover_pct", "Turnover %", "Turnover %"),
    num("masse_salariale_xaf", "Masse salariale", "Payroll"),
  ],
};

