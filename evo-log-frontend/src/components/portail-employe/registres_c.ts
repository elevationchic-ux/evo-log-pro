/**
 * Configs Registre pour portail-employe (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-employe");

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

export const registreEmpLeaveRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "leave_request",
  tcode: "registre-leave-requests",
  icon: Icons.CalendarDays,
  titre: "Demandes de conges",
  titreEn: "Leave requests",
  description: "Demande de conge saisie par le collaborateur.",
  descriptionEn: "Leave request raised by the employee.",
  aide: "Les dates et le solde restant encadrent la demande.",
  aideEn: "Dates and remaining balance frame the request.",
  lister: (params) => api.lister("emp-leave-requests", params),
  creer: (data) => api.creer("emp-leave-requests", data),
  modifier: (id, data) => api.modifier("emp-leave-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("type_conge", "Type", "Leave type"),
    col("debut", "Debut", "Start"),
    col("fin", "Fin", "End"),
    col("jours", "Jours", "Days"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("type_conge", "Type", "Leave type"),
    dt("debut", "Debut", "Start"),
    dt("fin", "Fin", "End"),
    num("jours", "Jours", "Days"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpTimesheetEntry: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "timesheet_entry",
  tcode: "registre-timesheet-entries",
  icon: Icons.Clock,
  titre: "Feuilles de temps",
  titreEn: "Timesheet entries",
  description: "Saisie quotidienne du temps de travail.",
  descriptionEn: "Daily work-time logging.",
  aide: "Le total hebdomadaire doit egaler le temps contractuel.",
  aideEn: "The weekly total must equal the contractual time.",
  lister: (params) => api.lister("emp-timesheet-entries", params),
  creer: (data) => api.creer("emp-timesheet-entries", data),
  modifier: (id, data) => api.modifier("emp-timesheet-entries", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("date", "Date", "Date"),
    col("heures", "Heures", "Hours"),
    col("projet", "Projet", "Project"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    dt("date", "Date", "Date"),
    num("heures", "Heures", "Hours"),
    txt("projet", "Projet", "Project"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpOvertimeRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "overtime_request",
  tcode: "registre-overtime-requests",
  icon: Icons.Hourglass,
  titre: "Demandes d' heures supplementaires",
  titreEn: "Overtime requests",
  description: "Demande de validation d' heures supplementaires.",
  descriptionEn: "Request to validate overtime hours.",
  aide: "Le contingent annuel borne les heures declarees.",
  aideEn: "The annual cap bounds the declared hours.",
  lister: (params) => api.lister("emp-overtime-requests", params),
  creer: (data) => api.creer("emp-overtime-requests", data),
  modifier: (id, data) => api.modifier("emp-overtime-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("minutes", "Minutes", "Minutes"),
    col("motif", "Motif", "Reason"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    num("minutes", "Minutes", "Minutes"),
    txt("motif", "Motif", "Reason"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpAttendanceCorrection: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "attendance_correction",
  tcode: "registre-attendance-corrections",
  icon: Icons.CalendarCheck,
  titre: "Regularisations de pointage",
  titreEn: "Attendance corrections",
  description: "Demande de correction d' un pointage errone ou oublie.",
  descriptionEn: "Request to fix a wrong or missed clock-in.",
  aide: "L' heure reellement effectuee est justifiee.",
  aideEn: "The actual worked time is justified.",
  lister: (params) => api.lister("emp-attendance-corrections", params),
  creer: (data) => api.creer("emp-attendance-corrections", data),
  modifier: (id, data) => api.modifier("emp-attendance-corrections", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("date_concernee", "Date concernee", "Affected date"),
    col("motif", "Motif", "Reason"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    dt("date_concernee", "Date concernee", "Affected date"),
    txt("motif", "Motif", "Reason"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpShiftSwap: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "shift_swap",
  tcode: "registre-shift-swaps",
  icon: Icons.ArrowLeftRight,
  titre: "Echanges de poste",
  titreEn: "Shift swaps",
  description: "Demande d' echange de poste entre deux collaborateurs.",
  descriptionEn: "Request to swap a shift between two employees.",
  aide: "L' accord des deux parties valide l' echange.",
  aideEn: "Both parties' agreement validates the swap.",
  lister: (params) => api.lister("emp-shift-swaps", params),
  creer: (data) => api.creer("emp-shift-swaps", data),
  modifier: (id, data) => api.modifier("emp-shift-swaps", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("demandeur", "Demandeur", "Requester"),
    col("partenaire", "Partenaire", "Partner"),
    col("date_poste", "Date du poste", "Shift date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("demandeur", "Demandeur", "Requester"),
    txt("partenaire", "Partenaire", "Partner"),
    dtx("date_poste", "Date du poste", "Shift date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpTrainingEnrollment: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "training_enrollment",
  tcode: "registre-training-enrollments",
  icon: Icons.GraduationCap,
  titre: "Inscriptions formation",
  titreEn: "Training enrollments",
  description: "Inscription d' un collaborateur a une action de formation.",
  descriptionEn: "Employee enrollment in a training action.",
  aide: "Le plan de formation et le budget encadrent l' inscription.",
  aideEn: "The training plan and budget frame the enrollment.",
  lister: (params) => api.lister("emp-training-enrollments", params),
  creer: (data) => api.creer("emp-training-enrollments", data),
  modifier: (id, data) => api.modifier("emp-training-enrollments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("formation", "Formation", "Training"),
    col("date_debut", "Debut", "Start"),
    col("organism", "Organisme", "Provider"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("formation", "Formation", "Training"),
    dt("date_debut", "Debut", "Start"),
    txt("organism", "Organisme", "Provider"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpSkillDeclaration: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "skill_declaration",
  tcode: "registre-skill-declarations",
  icon: Icons.Star,
  titre: "Declarations de competences",
  titreEn: "Skill declarations",
  description: "Auto-declaration d' une competence par le collaborateur.",
  descriptionEn: "Self-declaration of a skill by the employee.",
  aide: "Le niveau declare est ensuite evalue par le manager.",
  aideEn: "The declared level is then assessed by the manager.",
  lister: (params) => api.lister("emp-skill-declarations", params),
  creer: (data) => api.creer("emp-skill-declarations", data),
  modifier: (id, data) => api.modifier("emp-skill-declarations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("competence", "Competence", "Skill"),
    col("niveau", "Niveau", "Level"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("competence", "Competence", "Skill"),
    txt("niveau", "Niveau", "Level"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpCertificationRenewal: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "certification_renewal",
  tcode: "registre-certification-renewals",
  icon: Icons.Award,
  titre: "Renouvellements de certification",
  titreEn: "Certification renewals",
  description: "Demande de renouvellement d' une certification / habilitation.",
  descriptionEn: "Request to renew a certification / authorization.",
  aide: "La date d' expiration impose l' anticipation.",
  aideEn: "The expiry date forces anticipation.",
  lister: (params) => api.lister("emp-certification-renewals", params),
  creer: (data) => api.creer("emp-certification-renewals", data),
  modifier: (id, data) => api.modifier("emp-certification-renewals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("certification", "Certification", "Certification"),
    col("expire_le", "Expire le", "Expires"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("certification", "Certification", "Certification"),
    dt("expire_le", "Expire le", "Expires"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpPersonalInfoChange: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "personal_info_change",
  tcode: "registre-personal-info-changes",
  icon: Icons.UserCog,
  titre: "Modifications d' etat civil",
  titreEn: "Personal info changes",
  description: "Demande de mise a jour d' une donnee personnelle.",
  descriptionEn: "Request to update a personal data item.",
  aide: "La piece justificative appuie la modification.",
  aideEn: "The supporting document backs the change.",
  lister: (params) => api.lister("emp-personal-info-changes", params),
  creer: (data) => api.creer("emp-personal-info-changes", data),
  modifier: (id, data) => api.modifier("emp-personal-info-changes", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("champ", "Champ modifie", "Changed field"),
    col("nouvelle_valeur", "Nouvelle valeur", "New value"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("champ", "Champ modifie", "Changed field"),
    txt("nouvelle_valeur", "Nouvelle valeur", "New value"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpBankDetailsUpdate: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "bank_details_update",
  tcode: "registre-bank-details-updates",
  icon: Icons.Wallet,
  titre: "Changements de RIB",
  titreEn: "Bank details updates",
  description: "Demande de changement du compte de versement de la paie.",
  descriptionEn: "Request to change the payroll bank account.",
  aide: "Un RIB valide atteste la securite du virement.",
  aideEn: "A validated RIB secures the transfer.",
  lister: (params) => api.lister("emp-bank-details-updates", params),
  creer: (data) => api.creer("emp-bank-details-updates", data),
  modifier: (id, data) => api.modifier("emp-bank-details-updates", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("banque", "Banque", "Bank"),
    col("date_effet", "Date d' effet", "Effective date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("banque", "Banque", "Bank"),
    dt("date_effet", "Date d' effet", "Effective date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpEmergencyContact: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "emergency_contact",
  tcode: "registre-emergency-contacts",
  icon: Icons.Phone,
  titre: "Contacts d' urgence",
  titreEn: "Emergency contacts",
  description: "Contact a prevenir en cas d' urgence pour le collaborateur.",
  descriptionEn: "Contact to alert in an emergency for the employee.",
  aide: "Le lien et le telephone rendent le contact actionnable.",
  aideEn: "Relationship and phone make the contact actionable.",
  lister: (params) => api.lister("emp-emergency-contacts", params),
  creer: (data) => api.creer("emp-emergency-contacts", data),
  modifier: (id, data) => api.modifier("emp-emergency-contacts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("nom", "Nom", "Name"),
    col("lien", "Lien", "Relationship"),
    col("telephone", "Telephone", "Phone"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("nom", "Nom", "Name"),
    txt("lien", "Lien", "Relationship"),
    txt("telephone", "Telephone", "Phone"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpBadgeRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "badge_request",
  tcode: "registre-badge-requests",
  icon: Icons.BadgeCheck,
  titre: "Demandes de badge",
  titreEn: "Badge requests",
  description: "Demande de badge d' acces ou de renouvellement.",
  descriptionEn: "Request for an access badge or renewal.",
  aide: "Le motif (nouveau / perte) declenche la fabrication.",
  aideEn: "The reason (new/lost) triggers fabrication.",
  lister: (params) => api.lister("emp-badge-requests", params),
  creer: (data) => api.creer("emp-badge-requests", data),
  modifier: (id, data) => api.modifier("emp-badge-requests", id, data),
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


export const registreEmpAccessRequest: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "access_request",
  tcode: "registre-access-requests",
  icon: Icons.KeyRound,
  titre: "Demandes d' acces",
  titreEn: "Access requests",
  description: "Demande d' acces a un systeme, un local ou un equipement.",
  descriptionEn: "Request for access to a system, room or equipment.",
  aide: "Le niveau d' acces est justifie par la fonction.",
  aideEn: "The access level is justified by the role.",
  lister: (params) => api.lister("emp-access-requests", params),
  creer: (data) => api.creer("emp-access-requests", data),
  modifier: (id, data) => api.modifier("emp-access-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("ressource", "Ressource", "Resource"),
    col("type_acces", "Type d' acces", "Access type"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("ressource", "Ressource", "Resource"),
    txt("type_acces", "Type d' acces", "Access type"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpDocumentUpload: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "document_upload",
  tcode: "registre-document-uploads",
  icon: Icons.Archive,
  titre: "Depot de documents RH",
  titreEn: "HR document uploads",
  description: "Depot par le collaborateur d' un piece demandee par les RH.",
  descriptionEn: "Employee upload of a document requested by HR.",
  aide: "La typologie et la validite structurent le dossier.",
  aideEn: "Typology and validity structure the file.",
  lister: (params) => api.lister("emp-document-uploads", params),
  creer: (data) => api.creer("emp-document-uploads", data),
  modifier: (id, data) => api.modifier("emp-document-uploads", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("type_piece", "Type de piece", "Document type"),
    col("fichier", "Fichier", "File"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("type_piece", "Type de piece", "Document type"),
    txt("fichier", "Fichier", "File"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpSelfReview: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "self_review",
  tcode: "registre-self-reviews",
  icon: Icons.ClipboardCheck,
  titre: "Auto-evaluations",
  titreEn: "Self reviews",
  description: "Auto-evaluation redigee par le collaborateur pour l' entretien annuel.",
  descriptionEn: "Self-assessment written for the annual review.",
  aide: "Les objectifs atteints sont auto-poses avant la revue manager.",
  aideEn: "Achieved goals are self-stated before the manager review.",
  lister: (params) => api.lister("emp-self-reviews", params),
  creer: (data) => api.creer("emp-self-reviews", data),
  modifier: (id, data) => api.modifier("emp-self-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("periode", "Periode", "Period"),
    col("accomplissements", "Accomplissements", "Achievements"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("periode", "Periode", "Period"),
    txt("accomplissements", "Accomplissements", "Achievements"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpMobilityApplication: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "mobility_application",
  tcode: "registre-internal-mobility-applications",
  icon: Icons.GitBranch,
  titre: "Candidatures internes",
  titreEn: "Internal mobility applications",
  description: "Candidature du collaborateur a un poste interne ouvert.",
  descriptionEn: "Employee application to an open internal position.",
  aide: "Le poste cible et la motivation structurent la candidature.",
  aideEn: "Target role and motivation frame the application.",
  lister: (params) => api.lister("emp-internal-mobility-applications", params),
  creer: (data) => api.creer("emp-internal-mobility-applications", data),
  modifier: (id, data) => api.modifier("emp-internal-mobility-applications", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("poste_cible", "Poste cible", "Target role"),
    col("motivation", "Motivation", "Motivation"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("poste_cible", "Poste cible", "Target role"),
    txt("motivation", "Motivation", "Motivation"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreEmpSicknessDeclaration: ConfigRegistre = {
  permModule: "rh",
  permSousModule: "sickness_declaration",
  tcode: "registre-sickness-declarations",
  icon: Icons.Stethoscope,
  titre: "Declarations d' arret maladie",
  titreEn: "Sickness declarations",
  description: "Declaration d' un arret de travail pour maladie par le collaborateur.",
  descriptionEn: "Employee declaration of a sick-leave stop.",
  aide: "La date et la duree de l' arret encadrent le controle.",
  aideEn: "The stop date and duration frame the control.",
  lister: (params) => api.lister("emp-sickness-declarations", params),
  creer: (data) => api.creer("emp-sickness-declarations", data),
  modifier: (id, data) => api.modifier("emp-sickness-declarations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("debut", "Debut", "Start"),
    col("duree_jours", "Duree (jours)", "Duration (days)"),
    col("justificatif", "Justificatif fourni", "Proof provided"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    dt("debut", "Debut", "Start"),
    num("duree_jours", "Duree (jours)", "Duration (days)"),
    chk("justificatif", "Justificatif fourni", "Proof provided"),
    txt("statut", "Statut", "Status"),
  ],
};

