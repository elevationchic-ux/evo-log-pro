/**
 * Configs Registre pour portail-qhse (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-qhse");

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

export const registreQspHazardReport: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "hazard_report",
  tcode: "registre-hazard-reports",
  icon: Icons.AlertTriangle,
  titre: "Signalements de dangers",
  titreEn: "Hazard reports",
  description: "Danger constate et signale par un operateur terrain.",
  descriptionEn: "Hazard observed and reported by a field operator.",
  aide: "La localisation et la gravite qualifient le danger.",
  aideEn: "Location and severity qualify the hazard.",
  lister: (params) => api.lister("qsp-hazard-reports", params),
  creer: (data) => api.creer("qsp-hazard-reports", data),
  modifier: (id, data) => api.modifier("qsp-hazard-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("lieu", "Lieu", "Location"),
    col("description", "Description", "Description"),
    col("gravite", "Gravite", "Severity"),
    col("signale_le", "Signale le", "Reported at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("lieu", "Lieu", "Location"),
    txt("description", "Description", "Description"),
    txt("gravite", "Gravite", "Severity"),
    dtx("signale_le", "Signale le", "Reported at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspNearMiss: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "near_miss",
  tcode: "registre-near-misses",
  icon: Icons.AlertOctagon,
  titre: "Presqu' accidents",
  titreEn: "Near misses",
  description: "Evenement sans dommage mais revelateur d' un risque.",
  descriptionEn: "Event without harm but revealing a risk.",
  aide: "Les presqu' accidents anticipent l' accident reel.",
  aideEn: "Near misses anticipate real accidents.",
  lister: (params) => api.lister("qsp-near-misses", params),
  creer: (data) => api.creer("qsp-near-misses", data),
  modifier: (id, data) => api.modifier("qsp-near-misses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("lieu", "Lieu", "Location"),
    col("situation", "Situation", "Situation"),
    col("date", "Date", "Date"),
    col("témoin", "Temoin", "Witness"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("lieu", "Lieu", "Location"),
    txt("situation", "Situation", "Situation"),
    dtx("date", "Date", "Date"),
    txt("témoin", "Temoin", "Witness"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspSafetyObservation: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "safety_observation",
  tcode: "registre-safety-observations",
  icon: Icons.Eye,
  titre: "Observations de securite",
  titreEn: "Safety observations",
  description: "Comportement ou situation observe lors d' une ronde securite.",
  descriptionEn: "Behavior or situation seen during a safety walk.",
  aide: "Positive ou a corriger : la nature pilote le suivi.",
  aideEn: "Positive or to correct: nature drives follow-up.",
  lister: (params) => api.lister("qsp-safety-observations", params),
  creer: (data) => api.creer("qsp-safety-observations", data),
  modifier: (id, data) => api.modifier("qsp-safety-observations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("zone", "Zone", "Zone"),
    col("observation", "Observation", "Observation"),
    col("nature", "Nature", "Nature"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("zone", "Zone", "Zone"),
    txt("observation", "Observation", "Observation"),
    txt("nature", "Nature", "Nature"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspPpeAttestation: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "ppe_attestation",
  tcode: "registre-ppe-attestations",
  icon: Icons.ShieldCheck,
  titre: "Attestations de port d' EPI",
  titreEn: "PPE attestations",
  description: "Attestation du port des EPI par l' operateur a une date.",
  descriptionEn: "Attestation of PPE wearing by the operator on a date.",
  aide: "Le controle atteste la conformite quotidienne.",
  aideEn: "The check evidences daily compliance.",
  lister: (params) => api.lister("qsp-ppe-attestations", params),
  creer: (data) => api.creer("qsp-ppe-attestations", data),
  modifier: (id, data) => api.modifier("qsp-ppe-attestations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("operateur", "Operateur", "Operator"),
    col("epi_controles", "EPI controles", "PPE checked"),
    col("conforme", "Conforme", "Compliant"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("operateur", "Operateur", "Operator"),
    num("epi_controles", "EPI controles", "PPE checked"),
    chk("conforme", "Conforme", "Compliant"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspToolboxTalk: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "toolbox_talk",
  tcode: "registre-toolbox-talks",
  icon: Icons.Megaphone,
  titre: "Quarts d' heure securite",
  titreEn: "Toolbox talks",
  description: "Briefe securite animee aupres d' une equipe.",
  descriptionEn: "Safety briefing held for a crew.",
  aide: "L' emargement atteste la diffusion du message.",
  aideEn: "The sign-in sheet evidences the message spread.",
  lister: (params) => api.lister("qsp-toolbox-talks", params),
  creer: (data) => api.creer("qsp-toolbox-talks", data),
  modifier: (id, data) => api.modifier("qsp-toolbox-talks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("sujet", "Sujet", "Topic"),
    col("anime_par", "Anime par", "Led by"),
    col("nb_participants", "Nb participants", "Participants"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("sujet", "Sujet", "Topic"),
    txt("anime_par", "Anime par", "Led by"),
    num("nb_participants", "Nb participants", "Participants"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspWorkPermitRequest: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "work_permit_request",
  tcode: "registre-work-permit-requests",
  icon: Icons.FileCheck2,
  titre: "Demandes de permis de travail",
  titreEn: "Work permit requests",
  description: "Demande d' autorisation pour une tache a risque.",
  descriptionEn: "Authorization request for a hazardous task.",
  aide: "La zone et le type conditionnent la validation.",
  aideEn: "Zone and type condition the approval.",
  lister: (params) => api.lister("qsp-work-permit-requests", params),
  creer: (data) => api.creer("qsp-work-permit-requests", data),
  modifier: (id, data) => api.modifier("qsp-work-permit-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("type", "Type", "Type"),
    col("lieu", "Lieu", "Location"),
    col("demandeur", "Demandeur", "Requester"),
    col("debut", "Debut", "Start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("type", "Type", "Type"),
    txt("lieu", "Lieu", "Location"),
    txt("demandeur", "Demandeur", "Requester"),
    dtx("debut", "Debut", "Start"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspSafetyTrainingLog: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "safety_training_log",
  tcode: "registre-safety-training-log",
  icon: Icons.GraduationCap,
  titre: "Suivi formation securite",
  titreEn: "Safety training log",
  description: "Participation d' un operateur a une formation securite.",
  descriptionEn: "Operator's participation in a safety training.",
  aide: "La validite du certificat conditionne l' habilitation.",
  aideEn: "Certificate validity conditions the authorization.",
  lister: (params) => api.lister("qsp-safety-training-log", params),
  creer: (data) => api.creer("qsp-safety-training-log", data),
  modifier: (id, data) => api.modifier("qsp-safety-training-log", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("operateur", "Operateur", "Operator"),
    col("formation", "Formation", "Training"),
    col("date", "Date", "Date"),
    col("validite", "Validite", "Validity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("operateur", "Operateur", "Operator"),
    txt("formation", "Formation", "Training"),
    dt("date", "Date", "Date"),
    dt("validite", "Validite", "Validity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspExposureRecord: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "exposure_record",
  tcode: "registre-exposure-records",
  icon: Icons.Activity,
  titre: "Registres d' exposition",
  titreEn: "Exposure records",
  description: "Exposition mesuree d' un operateur a un agent nocif.",
  descriptionEn: "Measured exposure of an operator to a harmful agent.",
  aide: "La valeur vs la VLEP determine la conformite.",
  aideEn: "Value vs limit determines compliance.",
  lister: (params) => api.lister("qsp-exposure-records", params),
  creer: (data) => api.creer("qsp-exposure-records", data),
  modifier: (id, data) => api.modifier("qsp-exposure-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("operateur", "Operateur", "Operator"),
    col("agent", "Agent", "Agent"),
    col("valeur", "Valeur mesuree", "Measured value"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("operateur", "Operateur", "Operator"),
    txt("agent", "Agent", "Agent"),
    num("valeur", "Valeur mesuree", "Measured value"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspFirstAidLog: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "first_aid_log",
  tcode: "registre-first-aid-log",
  icon: Icons.Cross,
  titre: "Registre de premiers secours",
  titreEn: "First aid log",
  description: "Intervention de premiers secours sur un collaborateur.",
  descriptionEn: "First-aid intervention on a coworker.",
  aide: "La gravite oriente l' orientation medicale.",
  aideEn: "Severity guides the medical direction.",
  lister: (params) => api.lister("qsp-first-aid-log", params),
  creer: (data) => api.creer("qsp-first-aid-log", data),
  modifier: (id, data) => api.modifier("qsp-first-aid-log", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("personne", "Personne", "Person"),
    col("nature_blessure", "Nature", "Injury nature"),
    col("date", "Date", "Date"),
    col("secouriste", "Secouriste", "First aider"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("personne", "Personne", "Person"),
    txt("nature_blessure", "Nature", "Injury nature"),
    dtx("date", "Date", "Date"),
    txt("secouriste", "Secouriste", "First aider"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspSafetySuggestion: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "safety_suggestion",
  tcode: "registre-safety-suggestions",
  icon: Icons.Lightbulb,
  titre: "Suggestions de securite",
  titreEn: "Safety suggestions",
  description: "Propose d' amelioration securite emise par un operateur.",
  descriptionEn: "Safety improvement proposed by an operator.",
  aide: "L' evaluation qualifie l' interet de la suggestion.",
  aideEn: "The evaluation qualifies the suggestion's value.",
  lister: (params) => api.lister("qsp-safety-suggestions", params),
  creer: (data) => api.creer("qsp-safety-suggestions", data),
  modifier: (id, data) => api.modifier("qsp-safety-suggestions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("auteur", "Auteur", "Author"),
    col("idee", "Ide", "Idea"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("auteur", "Auteur", "Author"),
    txt("idee", "Ide", "Idea"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspStopWorkAuthority: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "stop_work",
  tcode: "registre-stop-work-authorities",
  icon: Icons.Ban,
  titre: "Droits de retrait",
  titreEn: "Stop work authorities",
  description: "Exercice du droit de retrait pour danger imminent.",
  descriptionEn: "Exercise of the right to withdraw for imminent danger.",
  aide: "La reprise exige la levee du danger.",
  aideEn: "Resumption requires the danger to be lifted.",
  lister: (params) => api.lister("qsp-stop-work-authorities", params),
  creer: (data) => api.creer("qsp-stop-work-authorities", data),
  modifier: (id, data) => api.modifier("qsp-stop-work-authorities", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("motif", "Motif", "Reason"),
    col("declenche_le", "Declenche le", "Triggered at"),
    col("reprise_le", "Reprise le", "Resumed at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("motif", "Motif", "Reason"),
    dtx("declenche_le", "Declenche le", "Triggered at"),
    dtx("reprise_le", "Reprise le", "Resumed at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspSpillReport: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "spill_report",
  tcode: "registre-spill-reports",
  icon: Icons.Droplets,
  titre: "Signalements de deversement",
  titreEn: "Spill reports",
  description: "Deversement accidentel de produit signale au QHSE.",
  descriptionEn: "Accidental product spill reported to QHSE.",
  aide: "Le volume et la nature definissent la decontamination.",
  aideEn: "Volume and nature define the decontamination.",
  lister: (params) => api.lister("qsp-spill-reports", params),
  creer: (data) => api.creer("qsp-spill-reports", data),
  modifier: (id, data) => api.modifier("qsp-spill-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("produit", "Produit", "Product"),
    col("volume", "Volume", "Volume"),
    col("lieu", "Lieu", "Location"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    num("volume", "Volume", "Volume"),
    txt("lieu", "Lieu", "Location"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspMsdsAck: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "msds_ack",
  tcode: "registre-msds-acknowledgements",
  icon: Icons.FileWarning,
  titre: "Accuses FDS",
  titreEn: "MSDS acknowledgements",
  description: "Prise de connaissance de la fiche de donnees de securite.",
  descriptionEn: "Reading of the safety data sheet.",
  aide: "L' accuse atteste la comprehension du produit.",
  aideEn: "The acknowledgement evidences understanding of the product.",
  lister: (params) => api.lister("qsp-msds-acknowledgements", params),
  creer: (data) => api.creer("qsp-msds-acknowledgements", data),
  modifier: (id, data) => api.modifier("qsp-msds-acknowledgements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("produit", "Produit", "Product"),
    col("operateur", "Operateur", "Operator"),
    col("date", "Date", "Date"),
    col("version_fds", "Version FDS", "SDS version"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    txt("operateur", "Operateur", "Operator"),
    dt("date", "Date", "Date"),
    txt("version_fds", "Version FDS", "SDS version"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspErgonomicsAssessment: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "ergonomics_assessment",
  tcode: "registre-ergonomics-assessments",
  icon: Icons.PersonStanding,
  titre: "Evaluations ergonomiques",
  titreEn: "Ergonomics assessments",
  description: "Evaluation ergonomique d' un poste de travail.",
  descriptionEn: "Ergonomic assessment of a workstation.",
  aide: "Le score de contrainte oriente amenagement.",
  aideEn: "The strain score guides the layout change.",
  lister: (params) => api.lister("qsp-ergonomics-assessments", params),
  creer: (data) => api.creer("qsp-ergonomics-assessments", data),
  modifier: (id, data) => api.modifier("qsp-ergonomics-assessments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("poste", "Poste", "Workstation"),
    col("contrainte", "Contrainte", "Strain"),
    col("score", "Score", "Score"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("poste", "Poste", "Workstation"),
    txt("contrainte", "Contrainte", "Strain"),
    num("score", "Score", "Score"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspHygieneCheck: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "hygiene_check",
  tcode: "registre-hygiene-checks",
  icon: Icons.SprayCan,
  titre: "Controles d' hygiene",
  titreEn: "Hygiene checks",
  description: "Controle d' hygiene d' un local ou d' un poste.",
  descriptionEn: "Hygiene check of a room or workstation.",
  aide: "La conformite conditionne l' usage du local.",
  aideEn: "Compliance conditions the room's use.",
  lister: (params) => api.lister("qsp-hygiene-checks", params),
  creer: (data) => api.creer("qsp-hygiene-checks", data),
  modifier: (id, data) => api.modifier("qsp-hygiene-checks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("local", "Local", "Room"),
    col("point_controle", "Point de controle", "Check point"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("local", "Local", "Room"),
    txt("point_controle", "Point de controle", "Check point"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspInspectionFinding: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "inspection_finding",
  tcode: "registre-inspection-findings",
  icon: Icons.SearchCheck,
  titre: "Constats d' inspection",
  titreEn: "Inspection findings",
  description: "Constat releve lors d' une inspection QHSE.",
  descriptionEn: "Finding raised during a QHSE inspection.",
  aide: "La non-conformite ouvre une action corrective.",
  aideEn: "The non-conformity opens a corrective action.",
  lister: (params) => api.lister("qsp-inspection-findings", params),
  creer: (data) => api.creer("qsp-inspection-findings", data),
  modifier: (id, data) => api.modifier("qsp-inspection-findings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("inspection", "Inspection", "Inspection"),
    col("constat", "Constat", "Finding"),
    col("criticite", "Criticite", "Criticality"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("inspection", "Inspection", "Inspection"),
    txt("constat", "Constat", "Finding"),
    txt("criticite", "Criticite", "Criticality"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspCapaReply: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "capa_reply",
  tcode: "registre-corrective-action-replies",
  icon: Icons.Reply,
  titre: "Reponses aux actions correctives",
  titreEn: "Corrective action replies",
  description: "Reponse d' un operateur a une action corrective qui lui est demandee.",
  descriptionEn: "Operator's reply to a corrective action assigned to them.",
  aide: "La preuve jointe valide la realisation de l' action.",
  aideEn: "The attached evidence validates the action.",
  lister: (params) => api.lister("qsp-corrective-action-replies", params),
  creer: (data) => api.creer("qsp-corrective-action-replies", data),
  modifier: (id, data) => api.modifier("qsp-corrective-action-replies", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("action_corrective", "Action corrective", "Corrective action"),
    col("reponse", "Reponse", "Reply"),
    col("operateur", "Operateur", "Operator"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("action_corrective", "Action corrective", "Corrective action"),
    txt("reponse", "Reponse", "Reply"),
    txt("operateur", "Operateur", "Operator"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspRiskAssessmentInput: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "risk_assessment_input",
  tcode: "registre-risk-assessment-inputs",
  icon: Icons.Target,
  titre: "Contributions a l' evaluation des risques",
  titreEn: "Risk assessment inputs",
  description: "Remontee terrain alimentant l' evaluation des risques d' un poste.",
  descriptionEn: "Field feed into the risk assessment of a task.",
  aide: "La frequence x gravite alimente la cotation.",
  aideEn: "Frequency x severity feeds the rating.",
  lister: (params) => api.lister("qsp-risk-assessment-inputs", params),
  creer: (data) => api.creer("qsp-risk-assessment-inputs", data),
  modifier: (id, data) => api.modifier("qsp-risk-assessment-inputs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("activite", "Activite", "Activity"),
    col("risque_identifie", "Risque identifie", "Identified risk"),
    col("cotation", "Cotation", "Rating"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("activite", "Activite", "Activity"),
    txt("risque_identifie", "Risque identifie", "Identified risk"),
    num("cotation", "Cotation", "Rating"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreQspEvacuationDrill: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "evacuation_drill",
  tcode: "registre-evacuation-drills",
  icon: Icons.Siren,
  titre: "Exercices d' evacuation",
  titreEn: "Evacuation drills",
  description: "Participation et chronometrage d' un operateur a un exercice d' evacuation.",
  descriptionEn: "Operator's participation and timing in an evacuation drill.",
  aide: "Le temps d' evacuation mesure evalue la performance.",
  aideEn: "The measured evacuation time assesses performance.",
  lister: (params) => api.lister("qsp-evacuation-drills", params),
  creer: (data) => api.creer("qsp-evacuation-drills", data),
  modifier: (id, data) => api.modifier("qsp-evacuation-drills", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("site", "Site", "Site"),
    col("date", "Date", "Date"),
    col("duree_sec", "Duree (s)", "Duration (s)"),
    col("nb_evacues", "Nb evacues", "Evacuees"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    dtx("date", "Date", "Date"),
    num("duree_sec", "Duree (s)", "Duration (s)"),
    num("nb_evacues", "Nb evacues", "Evacuees"),
    txt("statut", "Statut", "Status"),
  ],
};

