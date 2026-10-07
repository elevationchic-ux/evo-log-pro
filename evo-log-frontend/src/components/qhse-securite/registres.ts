/**
 * Configs Registre pour qhse-securite (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("qhse-securite");

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

export const registreEnvironmentalMeasurement: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "environmental",
  tcode: "registre-environmental-monitoring",
  icon: Icons.Activity,
  titre: "Suivi environnemental",
  titreEn: "Environmental monitoring",
  description: "Bruit, air, eau.",
  descriptionEn: "Noise, air, water.",
  aide: "Comparaison aux normes ICPE / OMS.",
  aideEn: "Compared to ICPE / WHO limits.",
  lister: (params) => api.lister("environmental-measurements", params),
  creer: (data) => api.creer("environmental-measurements", data),
  modifier: (id, data) => api.modifier("environmental-measurements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_relevé", "Type", "Type"),
    col("polluant", "Polluant", "Pollutant"),
    col("valeur", "Valeur", "Value"),
    col("unite", "Unite", "Unit"),
    col("norme_max", "Norme max", "Max threshold"),
    col("station", "Station", "Station"),
    col("date_relevé", "Date", "Date"),
    col("conformite", "Conformite", "Compliance"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_relevé", "Type", "Type", "type_relevé"),
    txt("polluant", "Polluant", "Pollutant"),
    num("valeur", "Valeur", "Value"),
    txt("unite", "Unite", "Unit"),
    num("norme_max", "Norme max", "Max threshold"),
    txt("station", "Station", "Station"),
    dtx("date_relevé", "Date", "Date"),
    sel("conformite", "Conformite", "Compliance", "conformite"),
  ],
};


export const registreWasteRecord: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "waste_management",
  tcode: "registre-waste-management",
  icon: Icons.Recycle,
  titre: "Gestion dechets / BSD",
  titreEn: "Waste management / BSW",
  description: "Bordereau de suivi dechet.",
  descriptionEn: "Waste tracking note.",
  aide: "Tracabilite BSD obligatoire.",
  aideEn: "BSW tracking mandatory.",
  lister: (params) => api.lister("waste-records", params),
  creer: (data) => api.creer("waste-records", data),
  modifier: (id, data) => api.modifier("waste-records", id, data),
  unicite: "numero_bsd",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_bsd", "Numero BSD", "BSW number", { searchable: true }),
    col("type_dechet", "Type dechet", "Waste type"),
    col("quantite_kg", "Quantite (kg)", "Quantity (kg)"),
    col("date_production", "Production", "Production date"),
    col("transporteur", "Transporteur", "Carrier"),
    col("destination", "Destination", "Destination"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_bsd", "Numero BSD", "BSW number", { obligatoire: true }),
    sel("type_dechet", "Type dechet", "Waste type", "type_dechet"),
    num("quantite_kg", "Quantite (kg)", "Quantity (kg)"),
    dt("date_production", "Production", "Production date"),
    txt("transporteur", "Transporteur", "Carrier"),
    txt("destination", "Destination", "Destination"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSafetyDataSheet: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "chemical_safety",
  tcode: "registre-chemical-safety",
  icon: Icons.FlaskConical,
  titre: "FDS et produits chimiques",
  titreEn: "SDS and chemicals",
  description: "Fiches de donnees de securite.",
  descriptionEn: "Safety data sheets.",
  aide: "Maj a chaque revision fournisseur.",
  aideEn: "Update on supplier revision.",
  lister: (params) => api.lister("safety-data-sheets", params),
  creer: (data) => api.creer("safety-data-sheets", data),
  modifier: (id, data) => api.modifier("safety-data-sheets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("nom_produit", "Nom produit", "Product name"),
    col("numero_ce", "Numero CE", "EC number"),
    col("fournisseur", "Fournisseur", "Supplier"),
    col("phrase_risque", "Phrases de risque", "Risk phrases"),
    col("version_fds", "Version FDS", "SDS version"),
    col("date_revision", "Revision", "Revision date"),
    col("classification", "Classification", "Classification"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("nom_produit", "Nom produit", "Product name"),
    txt("numero_ce", "Numero CE", "EC number"),
    txt("fournisseur", "Fournisseur", "Supplier"),
    txt("phrase_risque", "Phrases de risque", "Risk phrases"),
    txt("version_fds", "Version FDS", "SDS version"),
    dt("date_revision", "Revision", "Revision date"),
    sel("classification", "Classification", "Classification", "classification"),
  ],
};


export const registreEmergencyPlan: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "emergency_plan",
  tcode: "registre-emergency-plans",
  icon: Icons.Siren,
  titre: "Plans d'urgence / exercices",
  titreEn: "Emergency plans and drills",
  description: "Evacuation, exercices annuels.",
  descriptionEn: "Evacuation, yearly drills.",
  aide: "Chaque exercice donne une fiche de retour.",
  aideEn: "Each drill yields a feedback sheet.",
  lister: (params) => api.lister("emergency-plans", params),
  creer: (data) => api.creer("emergency-plans", data),
  modifier: (id, data) => api.modifier("emergency-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_plan", "Type", "Type"),
    col("zone_concernee", "Zone concernee", "Zone"),
    col("date_elaboration", "Elaboration", "Preparation date"),
    col("date_dernier_exercice", "Dernier exercice", "Last drill"),
    col("frequence_exercice_mois", "Frequence exercice (mois)", "Drill frequency (months)"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_plan", "Type", "Type", "type_plan"),
    txt("zone_concernee", "Zone concernee", "Zone"),
    dt("date_elaboration", "Elaboration", "Preparation date"),
    dt("date_dernier_exercice", "Dernier exercice", "Last drill"),
    num("frequence_exercice_mois", "Frequence exercice (mois)", "Drill frequency (months)"),
  ],
};


export const registrePpeItem: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "ppe_tracking",
  tcode: "registre-ppe-tracking",
  icon: Icons.HardHat,
  titre: "EPI equipements protection",
  titreEn: "PPE",
  description: "Dotation EPI par employe.",
  descriptionEn: "PPE per employee.",
  aide: "Renouvellement auto a expiration.",
  aideEn: "Auto-renew on expiry.",
  lister: (params) => api.lister("ppe-items", params),
  creer: (data) => api.creer("ppe-items", data),
  modifier: (id, data) => api.modifier("ppe-items", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("type_epi", "Type EPI", "PPE type"),
    col("taille", "Taille", "Size"),
    col("date_attribution", "Attribution", "Issuance date"),
    col("date_expiration", "Expiration", "Expiry"),
    col("quantite", "Quantite", "Quantity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    sel("type_epi", "Type EPI", "PPE type", "type_epi"),
    txt("taille", "Taille", "Size"),
    dt("date_attribution", "Attribution", "Issuance date"),
    dt("date_expiration", "Expiration", "Expiry"),
    num("quantite", "Quantite", "Quantity"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreHealthVisit: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "occupational_health",
  tcode: "registre-occupational-health",
  icon: Icons.Stethoscope,
  titre: "Medecine du travail",
  titreEn: "Occupational health",
  description: "Visites médicales obligatoires.",
  descriptionEn: "Mandatory medical visits.",
  aide: "Report si inaptitude.",
  aideEn: "Report if unfit.",
  lister: (params) => api.lister("health-visits", params),
  creer: (data) => api.creer("health-visits", data),
  modifier: (id, data) => api.modifier("health-visits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("employe_id", "Employe", "Employee"),
    col("type_visite", "Type visite", "Visit type"),
    col("date_visite", "Date visite", "Visit date"),
    col("medecin", "Medecin", "Doctor"),
    col("resultat", "Resultat", "Result"),
    col("prochaine_visite", "Prochaine visite", "Next visit"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("employe_id", "Employe", "Employee"),
    sel("type_visite", "Type visite", "Visit type", "type_visite"),
    dt("date_visite", "Date visite", "Visit date"),
    txt("medecin", "Medecin", "Doctor"),
    sel("resultat", "Resultat", "Result", "resultat"),
    dt("prochaine_visite", "Prochaine visite", "Next visit"),
  ],
};


export const registreRiskAssessment: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "risk_assessment",
  tcode: "registre-risk-assessment",
  icon: Icons.ShieldAlert,
  titre: "Evaluation des risques (DUER)",
  titreEn: "Risk assessment (DUER)",
  description: "Document unique evaluation des risques.",
  descriptionEn: "Single risk assessment document.",
  aide: "Revue annuelle obligatoire.",
  aideEn: "Annual review mandatory.",
  lister: (params) => api.lister("risk-assessments", params),
  creer: (data) => api.creer("risk-assessments", data),
  modifier: (id, data) => api.modifier("risk-assessments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("unite_travail", "Unite de travail", "Work unit"),
    col("description_risque", "Description risque", "Risk description"),
    col("cotation", "Cotation", "Rating"),
    col("mesure_prevention", "Mesure prevention", "Prevention measure"),
    col("date_evaluation", "Evaluation", "Assessment date"),
    col("responsable", "Responsable", "Owner"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("unite_travail", "Unite de travail", "Work unit"),
    txt("description_risque", "Description risque", "Risk description"),
    sel("cotation", "Cotation", "Rating", "cotation"),
    txt("mesure_prevention", "Mesure prevention", "Prevention measure"),
    dt("date_evaluation", "Evaluation", "Assessment date"),
    txt("responsable", "Responsable", "Owner"),
  ],
};


export const registreCorrectiveAction: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "corrective_action",
  tcode: "registre-corrective-actions",
  icon: Icons.CheckCircle,
  titre: "Actions correctives / 8D",
  titreEn: "Corrective actions / 8D",
  description: "Suites a incidents ou non-conformites.",
  descriptionEn: "Follow-up to incidents or non-conformities.",
  aide: "Cloture = preuve d'efficacite.",
  aideEn: "Closure = proof of effectiveness.",
  lister: (params) => api.lister("corrective-actions", params),
  creer: (data) => api.creer("corrective-actions", data),
  modifier: (id, data) => api.modifier("corrective-actions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("source_ecart", "Source ecart", "Source deviation"),
    col("description_probleme", "Description probleme", "Problem description"),
    col("cause_racine", "Cause racine", "Root cause"),
    col("action_corrective", "Action corrective", "Corrective action"),
    col("responsable", "Responsable", "Owner"),
    col("date_prevue_cloture", "Cloture prevue", "Planned closure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("source_ecart", "Source ecart", "Source deviation"),
    txt("description_probleme", "Description probleme", "Problem description"),
    txt("cause_racine", "Cause racine", "Root cause"),
    txt("action_corrective", "Action corrective", "Corrective action"),
    txt("responsable", "Responsable", "Owner"),
    dt("date_prevue_cloture", "Cloture prevue", "Planned closure"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreManagementReview: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "management_review",
  tcode: "registre-management-reviews",
  icon: Icons.Presentation,
  titre: "Revues de direction",
  titreEn: "Management reviews",
  description: "Revue annuelle du systeme QHSE.",
  descriptionEn: "Annual QHSE review.",
  aide: "PV diffuse a tous les pilotes.",
  aideEn: "Minutes shared with all owners.",
  lister: (params) => api.lister("management-reviews", params),
  creer: (data) => api.creer("management-reviews", data),
  modifier: (id, data) => api.modifier("management-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("date_revue", "Date revue", "Review date"),
    col("participants", "Participants", "Participants"),
    col("sujets", "Sujets", "Topics"),
    col("decisions", "Decisions", "Decisions"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    dt("date_revue", "Date revue", "Review date"),
    txt("participants", "Participants", "Participants"),
    txt("sujets", "Sujets", "Topics"),
    txt("decisions", "Decisions", "Decisions"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreComplianceRecord: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "regulatory_compliance",
  tcode: "registre-regulatory-compliance",
  icon: Icons.Scale,
  titre: "Conformite reglementaire",
  titreEn: "Regulatory compliance",
  description: "Veille et preuves de conformite.",
  descriptionEn: "Watch and compliance evidence.",
  aide: "Alerte avant echeance declaration.",
  aideEn: "Alert before declaration deadline.",
  lister: (params) => api.lister("compliance-records", params),
  creer: (data) => api.creer("compliance-records", data),
  modifier: (id, data) => api.modifier("compliance-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("regulation", "Regulation", "Regulation"),
    col("domaine", "Domaine", "Domain"),
    col("obligation", "Obligation", "Obligation"),
    col("preuve", "Preuve", "Evidence"),
    col("date_constat", "Date constat", "Assessment date"),
    col("prochaine_echeance", "Prochaine echeance", "Next deadline"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("regulation", "Regulation", "Regulation"),
    sel("domaine", "Domaine", "Domain", "domaine"),
    txt("obligation", "Obligation", "Obligation"),
    txt("preuve", "Preuve", "Evidence"),
    dt("date_constat", "Date constat", "Assessment date"),
    dt("prochaine_echeance", "Prochaine echeance", "Next deadline"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreQualityAudit: ConfigRegistre = {
  permModule: "qhse",
  permSousModule: "quality_audit",
  tcode: "registre-quality-audits",
  icon: Icons.Search,
  titre: "Audits internes qualite",
  titreEn: "Internal quality audits",
  description: "Audits ISO 9001 / 14001.",
  descriptionEn: "ISO 9001 / 14001 audits.",
  aide: "Rapport + suivi des ecarts.",
  aideEn: "Report + gap tracking.",
  lister: (params) => api.lister("quality-audits", params),
  creer: (data) => api.creer("quality-audits", data),
  modifier: (id, data) => api.modifier("quality-audits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("type_audit", "Type audit", "Audit type"),
    col("perimetre", "Perimetre", "Scope"),
    col("auditeur", "Auditeur", "Auditor"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("nb_ecarts", "Nb ecarts", "Findings"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("type_audit", "Type audit", "Audit type", "type_audit"),
    txt("perimetre", "Perimetre", "Scope"),
    txt("auditeur", "Auditeur", "Auditor"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    num("nb_ecarts", "Nb ecarts", "Findings"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};

