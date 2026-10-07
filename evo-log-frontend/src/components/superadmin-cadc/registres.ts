/**
 * Configs Registre pour superadmin-cadc (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("superadmin-cadc");

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

export const registrePlatformAudit: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "platform_audit",
  tcode: "registre-platform-audit",
  icon: Icons.ScanSearch,
  titre: "Audit global plateforme multi-tenant",
  titreEn: "Global platform audit",
  description: "Revues croisees de la plateforme.",
  descriptionEn: "Cross-platform reviews.",
  aide: "Trimestriel.",
  aideEn: "Quarterly.",
  lister: (params) => api.lister("platform-audits", params),
  creer: (data) => api.creer("platform-audits", data),
  modifier: (id, data) => api.modifier("platform-audits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("periode_debut", "Debut", "Start"),
    col("periode_fin", "Fin", "End"),
    col("nb_tenants_audites", "Tenants audites", "Tenants audited"),
    col("constats", "Constats", "Findings"),
    col("recommandations", "Recommandations", "Recommendations"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    dt("periode_debut", "Debut", "Start"),
    dt("periode_fin", "Fin", "End"),
    num("nb_tenants_audites", "Tenants audites", "Tenants audited"),
    txt("constats", "Constats", "Findings"),
    txt("recommandations", "Recommandations", "Recommendations"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreComplianceDashboard: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "compliance_dashboards",
  tcode: "registre-compliance-dashboards",
  icon: Icons.Shield,
  titre: "Tableaux conformite globale",
  titreEn: "Global compliance dashboards",
  description: "Suivi conformite multi-tenant.",
  descriptionEn: "Cross-tenant compliance.",
  aide: "Diffusion quarterly.",
  aideEn: "Quarterly distribution.",
  lister: (params) => api.lister("compliance-dashboards", params),
  creer: (data) => api.creer("compliance-dashboards", data),
  modifier: (id, data) => api.modifier("compliance-dashboards", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("domaine", "Domaine", "Domain"),
    col("nb_tenants_conformes", "Tenants conformes", "Compliant tenants"),
    col("nb_tenants_hors", "Tenants hors", "Non-compliant tenants"),
    col("score_global_pct", "Score global %", "Overall score %"),
    col("date_revue", "Revue", "Review date"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("domaine", "Domaine", "Domain", "domaine"),
    num("nb_tenants_conformes", "Tenants conformes", "Compliant tenants"),
    num("nb_tenants_hors", "Tenants hors", "Non-compliant tenants"),
    num("score_global_pct", "Score global %", "Overall score %"),
    dt("date_revue", "Revue", "Review date"),
  ],
};


export const registreRetentionPolicy: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "data_retention",
  tcode: "registre-data-retention",
  icon: Icons.Trash,
  titre: "Politique retention / purge",
  titreEn: "Retention and purge policy",
  description: "Durees et modalites de purge.",
  descriptionEn: "Duration and purge rules.",
  aide: "Automatise via cron mensuel.",
  aideEn: "Automated via monthly cron.",
  lister: (params) => api.lister("retention-policies", params),
  creer: (data) => api.creer("retention-policies", data),
  modifier: (id, data) => api.modifier("retention-policies", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("categorie", "Categorie", "Category"),
    col("duree_conservation_jours", "Duree (j)", "Duration (d)"),
    col("methode_purge", "Methode purge", "Purge method"),
    col("base_legale", "Base legale", "Legal basis"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("categorie", "Categorie", "Category", "categorie"),
    num("duree_conservation_jours", "Duree (j)", "Duration (d)"),
    sel("methode_purge", "Methode purge", "Purge method", "methode_purge"),
    txt("base_legale", "Base legale", "Legal basis"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registrePlatformIncident: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "incident_response",
  tcode: "registre-incident-response",
  icon: Icons.AlertOctagon,
  titre: "Reponse incidents plateforme",
  titreEn: "Platform incident response",
  description: "Gestion crise et post-mortem.",
  descriptionEn: "Crisis and post-mortem.",
  aide: "Escalade P1 < 15 min.",
  aideEn: "P1 escalation under 15 min.",
  lister: (params) => api.lister("platform-incidents", params),
  creer: (data) => api.creer("platform-incidents", data),
  modifier: (id, data) => api.modifier("platform-incidents", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("titre", "Titre", "Title"),
    col("priorite", "Priorite", "Priority"),
    col("date_debut", "Debut", "Start"),
    col("date_resolution", "Resolution", "Resolution"),
    col("impact_tenants", "Impact tenants", "Tenants impacted"),
    col("cause_racine", "Cause racine", "Root cause"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("titre", "Titre", "Title"),
    sel("priorite", "Priorite", "Priority", "priorite"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_resolution", "Resolution", "Resolution"),
    txt("impact_tenants", "Impact tenants", "Tenants impacted"),
    txt("cause_racine", "Cause racine", "Root cause"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreAccessReview: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "access_review",
  tcode: "registre-access-reviews",
  icon: Icons.ShieldCheck,
  titre: "Revue periodique des acces",
  titreEn: "Periodic access review",
  description: "Certification des droits utilisateurs.",
  descriptionEn: "User rights certification.",
  aide: "Semestrielle par tenant.",
  aideEn: "Semi-annual per tenant.",
  lister: (params) => api.lister("access-reviews", params),
  creer: (data) => api.creer("access-reviews", data),
  modifier: (id, data) => api.modifier("access-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("tenant_id", "Tenant", "Tenant"),
    col("date_revue", "Date revue", "Review date"),
    col("nb_utilisateurs_revus", "Utilisateurs revus", "Users reviewed"),
    col("nb_droits_retires", "Droits retires", "Rights removed"),
    col("revue_par", "Revue par", "Reviewed by"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("tenant_id", "Tenant", "Tenant"),
    dt("date_revue", "Date revue", "Review date"),
    num("nb_utilisateurs_revus", "Utilisateurs revus", "Users reviewed"),
    num("nb_droits_retires", "Droits retires", "Rights removed"),
    txt("revue_par", "Revue par", "Reviewed by"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSoftwareLicense: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "license_management",
  tcode: "registre-license-management",
  icon: Icons.Award,
  titre: "Gestion licences et modules",
  titreEn: "License and module management",
  description: "Suivi des droits d'usage par module.",
  descriptionEn: "Track usage rights per module.",
  aide: "Renouvellement anticipe 60j.",
  aideEn: "Renew 60d before expiry.",
  lister: (params) => api.lister("software-licenses", params),
  creer: (data) => api.creer("software-licenses", data),
  modifier: (id, data) => api.modifier("software-licenses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("module", "Module", "Module"),
    col("editeur", "Editeur", "Vendor"),
    col("nb_sieges", "Sieges", "Seats"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("cotisation_xaf", "Cotisation XAF", "Fee XAF"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("module", "Module", "Module"),
    txt("editeur", "Editeur", "Vendor"),
    num("nb_sieges", "Sieges", "Seats"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    num("cotisation_xaf", "Cotisation XAF", "Fee XAF"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreTechnologyPartner: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "partner_network",
  tcode: "registre-partner-network",
  icon: Icons.Handshake,
  titre: "Reseau partenaires technologiques",
  titreEn: "Technology partner network",
  description: "Partenaires editeurs / integrateurs.",
  descriptionEn: "Editor / integrator partners.",
  aide: "Revue annuelle.",
  aideEn: "Annual review.",
  lister: (params) => api.lister("technology-partners", params),
  creer: (data) => api.creer("technology-partners", data),
  modifier: (id, data) => api.modifier("technology-partners", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("nom", "Nom", "Name"),
    col("type_partenaire", "Type", "Type"),
    col("produit_associe", "Produit associe", "Related product"),
    col("contrat", "Contrat", "Contract"),
    col("date_debut", "Debut", "Start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("nom", "Nom", "Name"),
    sel("type_partenaire", "Type", "Type", "type_partenaire"),
    txt("produit_associe", "Produit associe", "Related product"),
    txt("contrat", "Contrat", "Contract"),
    dt("date_debut", "Debut", "Start"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSaasRevenueRecord: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "revenue_analytics",
  tcode: "registre-revenue-analytics",
  icon: Icons.DollarSign,
  titre: "Analytique revenus SaaS / MRR",
  titreEn: "SaaS revenue / MRR analytics",
  description: "MRR, churn, ARPU, expansion.",
  descriptionEn: "MRR, churn, ARPU, expansion.",
  aide: "Revue mensuelle direction.",
  aideEn: "Monthly leadership review.",
  lister: (params) => api.lister("saas-revenue-records", params),
  creer: (data) => api.creer("saas-revenue-records", data),
  modifier: (id, data) => api.modifier("saas-revenue-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("mois", "Mois", "Month"),
    col("mrr_xaf", "MRR XAF", "MRR XAF"),
    col("churn_mrr_xaf", "Churn MRR", "Churn MRR"),
    col("expansion_mrr_xaf", "Expansion MRR", "Expansion MRR"),
    col("arpu_xaf", "ARPU", "ARPU"),
    col("nb_customers", "Nb clients", "Customer count"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("mois", "Mois", "Month"),
    num("mrr_xaf", "MRR XAF", "MRR XAF"),
    num("churn_mrr_xaf", "Churn MRR", "Churn MRR"),
    num("expansion_mrr_xaf", "Expansion MRR", "Expansion MRR"),
    num("arpu_xaf", "ARPU", "ARPU"),
    num("nb_customers", "Nb clients", "Customer count"),
  ],
};


export const registreGlobalConfigSetting: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "system_config",
  tcode: "registre-system-config",
  icon: Icons.Settings,
  titre: "Configuration systeme globale",
  titreEn: "Global system configuration",
  description: "Parametres transverses plateforme.",
  descriptionEn: "Cross-platform settings.",
  aide: "4-yeyes obligatoire.",
  aideEn: "Four-eyes mandatory.",
  lister: (params) => api.lister("global-config-settings", params),
  creer: (data) => api.creer("global-config-settings", data),
  modifier: (id, data) => api.modifier("global-config-settings", id, data),
  unicite: "code_setting",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_setting", "Code setting", "Setting code", { searchable: true }),
    col("valeur", "Valeur", "Value"),
    col("categorie", "Categorie", "Category"),
    col("description", "Description", "Description"),
    col("modifie_par", "Modifie par", "Modified by"),
    col("date_modif", "Date modif", "Modification date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_setting", "Code setting", "Setting code", { obligatoire: true }),
    txt("valeur", "Valeur", "Value"),
    sel("categorie", "Categorie", "Category", "categorie"),
    txt("description", "Description", "Description"),
    txt("modifie_par", "Modifie par", "Modified by"),
    dtx("date_modif", "Date modif", "Modification date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreDrPlan: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "disaster_recovery",
  tcode: "registre-disaster-recovery",
  icon: Icons.LifeBuoy,
  titre: "Plan reprise activite",
  titreEn: "Business continuity plan",
  description: "Scenario, RTO, RPO.",
  descriptionEn: "Scenario, RTO, RPO.",
  aide: "Test annuel obligatoire.",
  aideEn: "Annual test mandatory.",
  lister: (params) => api.lister("dr-plans", params),
  creer: (data) => api.creer("dr-plans", data),
  modifier: (id, data) => api.modifier("dr-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("scenario", "Scenario", "Scenario"),
    col("rto_heures", "RTO (h)", "RTO (h)"),
    col("rpo_minutes", "RPO (min)", "RPO (min)"),
    col("solution_secours", "Solution secours", "Failover solution"),
    col("date_dernier_test", "Dernier test", "Last test"),
    col("resultat_test", "Resultat test", "Test result"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    sel("scenario", "Scenario", "Scenario", "scenario"),
    num("rto_heures", "RTO (h)", "RTO (h)"),
    num("rpo_minutes", "RPO (min)", "RPO (min)"),
    txt("solution_secours", "Solution secours", "Failover solution"),
    dt("date_dernier_test", "Dernier test", "Last test"),
    sel("resultat_test", "Resultat test", "Test result", "resultat_test"),
  ],
};

