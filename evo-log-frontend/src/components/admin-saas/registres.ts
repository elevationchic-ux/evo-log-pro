/**
 * Configs Registre pour admin-saas (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("admin-saas");

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

export const registreFeatureFlag: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "feature_flag",
  tcode: "registre-feature-flags",
  icon: Icons.ToggleRight,
  titre: "Gestion fonctionnalites par tenant",
  titreEn: "Feature flags per tenant",
  description: "Active / desactive fonctionnalites.",
  descriptionEn: "Toggle features.",
  aide: "Revue mensuelle produit.",
  aideEn: "Monthly product review.",
  lister: (params) => api.lister("feature-flags", params),
  creer: (data) => api.creer("feature-flags", data),
  modifier: (id, data) => api.modifier("feature-flags", id, data),
  unicite: "code_flag",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_flag", "Code flag", "Flag code"),
    col("description", "Description", "Description"),
    col("actif", "Actif", "Active"),
    col("tenants_concernes", "Tenants concerns", "Tenants affected"),
    col("date_debut_rollout", "Debut rollout", "Rollout start"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_flag", "Code flag", "Flag code", { requisCreation: true }),
    txt("description", "Description", "Description"),
    chk("actif", "Actif", "Active"),
    txt("tenants_concernes", "Tenants concerns", "Tenants affected"),
    dt("date_debut_rollout", "Debut rollout", "Rollout start"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreApiQuota: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "rate_limit",
  tcode: "registre-rate-limiting",
  icon: Icons.Gauge,
  titre: "Quotas API et limitations",
  titreEn: "API quotas and limits",
  description: "Appels par tenant / minute.",
  descriptionEn: "Calls per tenant / minute.",
  aide: "Revise selon contrat.",
  aideEn: "Reviewed per contract.",
  lister: (params) => api.lister("api-quotas", params),
  creer: (data) => api.creer("api-quotas", data),
  modifier: (id, data) => api.modifier("api-quotas", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("api_group", "Groupe API", "API group"),
    col("limite_minute", "Limite minute", "Per-minute limit"),
    col("limite_jour", "Limite jour", "Daily limit"),
    col("consommation_actuelle", "Consommation actuelle", "Current usage"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    txt("api_group", "Groupe API", "API group"),
    num("limite_minute", "Limite minute", "Per-minute limit"),
    num("limite_jour", "Limite jour", "Daily limit"),
    num("consommation_actuelle", "Consommation actuelle", "Current usage"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreWhiteLabel: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "white_label",
  tcode: "registre-white-label",
  icon: Icons.Palette,
  titre: "Personnalisation marque",
  titreEn: "Branding customization",
  description: "Logo, domaine, couleur par tenant.",
  descriptionEn: "Logo, domain, color per tenant.",
  aide: "Valide par direction marketing.",
  aideEn: "Approved by marketing lead.",
  lister: (params) => api.lister("white-labels", params),
  creer: (data) => api.creer("white-labels", data),
  modifier: (id, data) => api.modifier("white-labels", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("nom_marque", "Nom marque", "Brand name"),
    col("domaine_personnalise", "Domaine", "Custom domain"),
    col("logo_url", "Logo URL", "Logo URL"),
    col("couleur_primaire", "Couleur primaire", "Primary color"),
    col("couleur_secondaire", "Couleur secondaire", "Secondary color"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    txt("nom_marque", "Nom marque", "Brand name"),
    txt("domaine_personnalise", "Domaine", "Custom domain"),
    txt("logo_url", "Logo URL", "Logo URL"),
    txt("couleur_primaire", "Couleur primaire", "Primary color"),
    txt("couleur_secondaire", "Couleur secondaire", "Secondary color"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registreTenantOnboarding: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "onboarding_wizard",
  tcode: "registre-onboarding-wizard",
  icon: Icons.Wand2,
  titre: "Parcours onboarding nouveau tenant",
  titreEn: "New tenant onboarding",
  description: "Etapes d'activation d'un nouveau client SaaS.",
  descriptionEn: "Activation steps for new SaaS clients.",
  aide: "Objectif : activation sous 14 jours.",
  aideEn: "Goal: activation under 14 days.",
  lister: (params) => api.lister("tenant-onboardings", params),
  creer: (data) => api.creer("tenant-onboardings", data),
  modifier: (id, data) => api.modifier("tenant-onboardings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("date_debut", "Debut", "Start"),
    col("date_activation", "Activation", "Activation"),
    col("nb_etapes_completes", "Etapes completes", "Steps done"),
    col("responsable_succeed", "Succeed", "Succeed"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    dt("date_debut", "Debut", "Start"),
    dt("date_activation", "Activation", "Activation"),
    num("nb_etapes_completes", "Etapes completes", "Steps done"),
    txt("responsable_succeed", "Succeed", "Succeed"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreTenantApiKey: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "api_key",
  tcode: "registre-api-keys",
  icon: Icons.KeyRound,
  titre: "Cles API tierces par tenant",
  titreEn: "Third-party API keys per tenant",
  description: "Cles d'acces aux webhooks tierces.",
  descriptionEn: "Access keys for third-party webhooks.",
  aide: "Rotation annuelle.",
  aideEn: "Annual rotation.",
  lister: (params) => api.lister("tenant-api-keys", params),
  creer: (data) => api.creer("tenant-api-keys", data),
  modifier: (id, data) => api.modifier("tenant-api-keys", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("label", "Label", "Label"),
    col("scopes", "Scopes", "Scopes"),
    col("date_creation", "Creation", "Creation"),
    col("date_expiration", "Expiration", "Expiry"),
    col("derniere_utilisation", "Derniere utilisation", "Last used"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    txt("label", "Label", "Label"),
    txt("scopes", "Scopes", "Scopes"),
    dt("date_creation", "Creation", "Creation"),
    dt("date_expiration", "Expiration", "Expiry"),
    dtx("derniere_utilisation", "Derniere utilisation", "Last used"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreTenantWebhook: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "webhook",
  tcode: "registre-webhooks",
  icon: Icons.Webhook,
  titre: "Integration evenements sortants",
  titreEn: "Outbound webhook integrations",
  description: "Evenements pousses vers tiers.",
  descriptionEn: "Events pushed to third parties.",
  aide: "Retries exponentiels 24h.",
  aideEn: "Exponential retries 24h.",
  lister: (params) => api.lister("tenant-webhooks", params),
  creer: (data) => api.creer("tenant-webhooks", data),
  modifier: (id, data) => api.modifier("tenant-webhooks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("url_destination", "URL", "URL"),
    col("evenements_abonnes", "Evenements abonnes", "Subscribed events"),
    col("secret_hmac", "Secret HMAC", "HMAC secret"),
    col("dernier_succes", "Dernier succes", "Last success"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    txt("url_destination", "URL", "URL"),
    txt("evenements_abonnes", "Evenements abonnes", "Subscribed events"),
    txt("secret_hmac", "Secret HMAC", "HMAC secret"),
    dtx("dernier_succes", "Dernier succes", "Last success"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreDataMigration: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "data_migration",
  tcode: "registre-data-migration",
  icon: Icons.Upload,
  titre: "Import / migration donnees",
  titreEn: "Data import and migration",
  description: "Import initial ou mise a jour.",
  descriptionEn: "Initial import or update.",
  aide: "Precheck et rollback obligatoires.",
  aideEn: "Precheck and rollback required.",
  lister: (params) => api.lister("data-migrations", params),
  creer: (data) => api.creer("data-migrations", data),
  modifier: (id, data) => api.modifier("data-migrations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("type_migration", "Type", "Type"),
    col("source", "Source", "Source"),
    col("nb_lignes_prevues", "Lignes prevues", "Expected rows"),
    col("nb_lignes_importees", "Lignes importees", "Imported rows"),
    col("nb_lignes_rejetees", "Lignes rejetees", "Rejected rows"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    sel("type_migration", "Type", "Type", "type_migration"),
    txt("source", "Source", "Source"),
    num("nb_lignes_prevues", "Lignes prevues", "Expected rows"),
    num("nb_lignes_importees", "Lignes importees", "Imported rows"),
    num("nb_lignes_rejetees", "Lignes rejetees", "Rejected rows"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registrePlatformTicket: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "support_ticket",
  tcode: "registre-support-tickets",
  icon: Icons.LifeBuoy,
  titre: "Tickets support plateforme",
  titreEn: "Platform support tickets",
  description: "Incidents et demandes support SaaS.",
  descriptionEn: "SaaS incidents and requests.",
  aide: "SLA premier reponse 4h.",
  aideEn: "First response SLA 4h.",
  lister: (params) => api.lister("platform-tickets", params),
  creer: (data) => api.creer("platform-tickets", data),
  modifier: (id, data) => api.modifier("platform-tickets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("titre", "Titre", "Title"),
    col("description", "Description", "Description"),
    col("priorite", "Priorite", "Priority"),
    col("assigne_a", "Assigne a", "Assigned to"),
    col("date_creation", "Creation", "Creation"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    txt("titre", "Titre", "Title"),
    txt("description", "Description", "Description"),
    sel("priorite", "Priorite", "Priority", "priorite"),
    txt("assigne_a", "Assigne a", "Assigned to"),
    dtx("date_creation", "Creation", "Creation"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreBillingEntry: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "billing_engine",
  tcode: "registre-billing-engine",
  icon: Icons.CreditCard,
  titre: "Moteur de facturation SaaS",
  titreEn: "SaaS billing engine",
  description: "Facturation par abonnement, usage, add-on.",
  descriptionEn: "Subscription, usage, add-on billing.",
  aide: "Reconcilie avec tresorerie.",
  aideEn: "Reconciled with treasury.",
  lister: (params) => api.lister("billing-entries", params),
  creer: (data) => api.creer("billing-entries", data),
  modifier: (id, data) => api.modifier("billing-entries", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("periode", "Periode", "Period"),
    col("type_facture", "Type facture", "Invoice type"),
    col("montant_ht_xaf", "Montant HT", "Amount excl. tax"),
    col("tva_xaf", "TVA", "VAT"),
    col("total_ttc_xaf", "Total TTC", "Total incl. tax"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    txt("periode", "Periode", "Period"),
    sel("type_facture", "Type facture", "Invoice type", "type_facture"),
    num("montant_ht_xaf", "Montant HT", "Amount excl. tax"),
    num("tva_xaf", "TVA", "VAT"),
    num("total_ttc_xaf", "Total TTC", "Total incl. tax"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreUsageAnalytics: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "usage_analytics",
  tcode: "registre-usage-analytics",
  icon: Icons.BarChart2,
  titre: "Analytique d'usage par tenant",
  titreEn: "Usage analytics per tenant",
  description: "Mesure actif / passif des fonctionnalites.",
  descriptionEn: "Track feature adoption.",
  aide: "Aide a la decision upsell / churn.",
  aideEn: "Supports upsell / churn decision.",
  lister: (params) => api.lister("usage-analytics", params),
  creer: (data) => api.creer("usage-analytics", data),
  modifier: (id, data) => api.modifier("usage-analytics", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant_id", "Tenant", "Tenant"),
    col("periode", "Periode", "Period"),
    col("utilisateurs_actifs", "Utilisateurs actifs", "Active users"),
    col("utilisateurs_seats", "Sieges", "Seats"),
    col("taux_adoption_pct", "Adoption %", "Adoption %"),
    col("score_sante", "Score sante", "Health score"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    num("tenant_id", "Tenant", "Tenant"),
    txt("periode", "Periode", "Period"),
    num("utilisateurs_actifs", "Utilisateurs actifs", "Active users"),
    num("utilisateurs_seats", "Sieges", "Seats"),
    num("taux_adoption_pct", "Adoption %", "Adoption %"),
    num("score_sante", "Score sante", "Health score"),
  ],
};


export const registreUptimeRecord: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "uptime_monitoring",
  tcode: "registre-uptime-monitoring",
  icon: Icons.Activity,
  titre: "Monitoring disponibilite / SLA",
  titreEn: "Uptime and SLA monitoring",
  description: "Sondage endpoints, latence, erreurs.",
  descriptionEn: "Endpoint probe, latency, errors.",
  aide: "Pinger toutes les minutes.",
  aideEn: "Ping every minute.",
  lister: (params) => api.lister("uptime-records", params),
  creer: (data) => api.creer("uptime-records", data),
  modifier: (id, data) => api.modifier("uptime-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("service", "Service", "Service"),
    col("region", "Region", "Region"),
    col("statut", "Statut", "Status"),
    col("latence_ms", "Latence (ms)", "Latency (ms)"),
    col("disponibilite_pct", "Disponibilite %", "Availability %"),
    col("date_mesure", "Date mesure", "Measurement date"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("service", "Service", "Service"),
    txt("region", "Region", "Region"),
    sel("statut", "Statut", "Status", "statut"),
    num("latence_ms", "Latence (ms)", "Latency (ms)"),
    num("disponibilite_pct", "Disponibilite %", "Availability %"),
    dtx("date_mesure", "Date mesure", "Measurement date"),
  ],
};

