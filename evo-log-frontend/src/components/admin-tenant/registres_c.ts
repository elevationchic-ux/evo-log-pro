/**
 * Configs Registre pour admin-tenant (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("admin-tenant");

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

export const registreAdmtDomainConfig: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "domain_config",
  tcode: "registre-domain-configs",
  icon: Icons.Globe,
  titre: "Configurations de domaine",
  titreEn: "Domain configs",
  description: "Nom de domaine rattache a un tenant.",
  descriptionEn: "Domain name attached to a tenant.",
  aide: "Un domaine verifie avec certificat SSL.",
  aideEn: "Verified domain with SSL certificate.",
  lister: (params) => api.lister("admtd-domain-configs", params),
  creer: (data) => api.creer("admtd-domain-configs", data),
  modifier: (id, data) => api.modifier("admtd-domain-configs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant", "Tenant", "Tenant"),
    col("domaine", "Domaine", "Domain"),
    col("type", "Type", "Type"),
    col("certificat_ssl", "Certificat SSL", "SSL certificate"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    txt("domaine", "Domaine", "Domain"),
    txt("type", "Type", "Type"),
    chk("certificat_ssl", "Certificat SSL", "SSL certificate"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtDnsRecord: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "dns_record",
  tcode: "registre-dns-records",
  icon: Icons.Network,
  titre: "Enregistrements DNS",
  titreEn: "DNS records",
  description: "Enregistrements DNS configures pour le tenant.",
  descriptionEn: "DNS records configured for the tenant.",
  aide: "TTL et valeur font la propagation.",
  aideEn: "TTL and value drive propagation.",
  lister: (params) => api.lister("admtd-dns-records", params),
  creer: (data) => api.creer("admtd-dns-records", data),
  modifier: (id, data) => api.modifier("admtd-dns-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom_hote", "Nom d'hote", "Hostname"),
    col("type_enregistrement", "Type", "Type"),
    col("valeur", "Valeur", "Value"),
    col("ttl_secondes", "TTL (s)", "TTL (s)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom_hote", "Nom d'hote", "Hostname"),
    txt("type_enregistrement", "Type", "Type"),
    txt("valeur", "Valeur", "Value"),
    num("ttl_secondes", "TTL (s)", "TTL (s)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtDataResidency: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "data_residency",
  tcode: "registre-data-residency",
  icon: Icons.Database,
  titre: "Souverainete des donnees",
  titreEn: "Data residency",
  description: "Localisation geographique et hebergement des donnees d' un tenant.",
  descriptionEn: "Geographic location and hosting of a tenant's data.",
  aide: "La region et la certification conditionnent la conformite.",
  aideEn: "Region and certification drive compliance.",
  lister: (params) => api.lister("admtd-data-residency", params),
  creer: (data) => api.creer("admtd-data-residency", data),
  modifier: (id, data) => api.modifier("admtd-data-residency", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant", "Tenant", "Tenant"),
    col("region", "Region", "Region"),
    col("hebergeur", "Hebergeur", "Host provider"),
    col("certification_conforme", "Certification conforme", "Certified compliant"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    txt("region", "Region", "Region"),
    txt("hebergeur", "Hebergeur", "Host provider"),
    chk("certification_conforme", "Certification conforme", "Certified compliant"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtFeatureEntitlement: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "feature_entitlement",
  tcode: "registre-feature-entitlements",
  icon: Icons.KeyRound,
  titre: "Droits fonctionnels",
  titreEn: "Feature entitlements",
  description: "Activation d' un module/fonction pour un tenant.",
  descriptionEn: "Activation of a module/feature for a tenant.",
  aide: "Limite et expiration bornent le droit.",
  aideEn: "Limit and expiry bound the entitlement.",
  lister: (params) => api.lister("admtd-feature-entitlements", params),
  creer: (data) => api.creer("admtd-feature-entitlements", data),
  modifier: (id, data) => api.modifier("admtd-feature-entitlements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("module", "Module", "Module"),
    col("actif", "Actif", "Active"),
    col("limite", "Limite", "Limit"),
    col("date_expiration", "Expiration", "Expiry date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("module", "Module", "Module"),
    chk("actif", "Actif", "Active"),
    num("limite", "Limite", "Limit"),
    dt("date_expiration", "Expiration", "Expiry date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtUsageQuota: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "usage_quota",
  tcode: "registre-usage-quotas",
  icon: Icons.Gauge,
  titre: "Quotas d' usage",
  titreEn: "Usage quotas",
  description: "Quota alloue et consomme par ressource pour un tenant.",
  descriptionEn: "Allocated and consumed quota per resource for a tenant.",
  aide: "La consommation ne doit pas depasser le quota.",
  aideEn: "Consumption must not exceed quota.",
  lister: (params) => api.lister("admtd-usage-quotas", params),
  creer: (data) => api.creer("admtd-usage-quotas", data),
  modifier: (id, data) => api.modifier("admtd-usage-quotas", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ressource", "Ressource", "Resource"),
    col("quota_autorise", "Quota autorise", "Allowed quota"),
    col("consomme", "Consomme", "Consumed"),
    col("periode", "Periode", "Period"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ressource", "Ressource", "Resource"),
    num("quota_autorise", "Quota autorise", "Allowed quota"),
    num("consomme", "Consomme", "Consumed"),
    txt("periode", "Periode", "Period"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtImpersonationLog: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "impersonation_log",
  tcode: "registre-impersonation-logs",
  icon: Icons.UserCog,
  titre: "Journaux d' impersonation",
  titreEn: "Impersonation logs",
  description: "Trace d' une session d' administration en tant qu' un tenant.",
  descriptionEn: "Trace of an admin session acting as a tenant.",
  aide: "Toute impersonation est motivee et bornee dans le temps.",
  aideEn: "Every impersonation is justified and time-bounded.",
  lister: (params) => api.lister("admtd-impersonation-logs", params),
  creer: (data) => api.creer("admtd-impersonation-logs", data),
  modifier: (id, data) => api.modifier("admtd-impersonation-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("admin", "Admin", "Admin"),
    col("cible_tenant", "Tenant cible", "Target tenant"),
    col("motif", "Motif", "Reason"),
    col("debut", "Debut", "Start"),
    col("fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("admin", "Admin", "Admin"),
    txt("cible_tenant", "Tenant cible", "Target tenant"),
    txt("motif", "Motif", "Reason"),
    dtx("debut", "Debut", "Start"),
    dtx("fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtOnboardingStep: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "onboarding_step",
  tcode: "registre-onboarding-steps",
  icon: Icons.ListChecks,
  titre: "Etapes d' onboarding",
  titreEn: "Onboarding steps",
  description: "Jalon du demarrage operationnel d' un nouveau tenant.",
  descriptionEn: "Milestone of a new tenant's operational go-live.",
  aide: "Ordre et responsable structurent le deploiement.",
  aideEn: "Order and owner structure rollout.",
  lister: (params) => api.lister("admtd-onboarding-steps", params),
  creer: (data) => api.creer("admtd-onboarding-steps", data),
  modifier: (id, data) => api.modifier("admtd-onboarding-steps", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant", "Tenant", "Tenant"),
    col("etape", "Etape", "Step"),
    col("ordre", "Ordre", "Order"),
    col("responsable", "Responsable", "Owner"),
    col("date_completion", "Date completion", "Completion date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    txt("etape", "Etape", "Step"),
    num("ordre", "Ordre", "Order"),
    txt("responsable", "Responsable", "Owner"),
    dt("date_completion", "Date completion", "Completion date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtWhiteLabelConfig: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "white_label_config",
  tcode: "registre-white-label-configs",
  icon: Icons.Palette,
  titre: "Configurations marque blanche",
  titreEn: "White-label configs",
  description: "Personnalisation de marque affichee pour un tenant.",
  descriptionEn: "Branding personalization shown to a tenant.",
  aide: "Nom, logo et couleur definissent l' habillage.",
  aideEn: "Name, logo and color define the skin.",
  lister: (params) => api.lister("admtd-white-label-configs", params),
  creer: (data) => api.creer("admtd-white-label-configs", data),
  modifier: (id, data) => api.modifier("admtd-white-label-configs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant", "Tenant", "Tenant"),
    col("nom_affiche", "Nom affiche", "Display name"),
    col("logo_url", "URL logo", "Logo URL"),
    col("couleur_principale", "Couleur principale", "Primary color"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    txt("nom_affiche", "Nom affiche", "Display name"),
    txt("logo_url", "URL logo", "Logo URL"),
    txt("couleur_principale", "Couleur principale", "Primary color"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtTenantBackup: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "tenant_backup",
  tcode: "registre-tenant-backups",
  icon: Icons.HardDrive,
  titre: "Sauvegardes tenant",
  titreEn: "Tenant backups",
  description: "Sauvegarde periodique des donnees d' un tenant.",
  descriptionEn: "Periodic backup of a tenant's data.",
  aide: "Taille, frequence et derniere reussite caracterisent la sauvegarde.",
  aideEn: "Size, cadence and last success characterize the backup.",
  lister: (params) => api.lister("admtd-tenant-backups", params),
  creer: (data) => api.creer("admtd-tenant-backups", data),
  modifier: (id, data) => api.modifier("admtd-tenant-backups", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant", "Tenant", "Tenant"),
    col("taille_octets", "Taille (octets)", "Size (bytes)"),
    col("frequence", "Frequence", "Cadence"),
    col("derniere_reussite", "Derniere reussite", "Last success"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    num("taille_octets", "Taille (octets)", "Size (bytes)"),
    txt("frequence", "Frequence", "Cadence"),
    dtx("derniere_reussite", "Derniere reussite", "Last success"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmtIntegrationWebhook: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "integration_webhook",
  tcode: "registre-integration-webhooks",
  icon: Icons.Webhook,
  titre: "Webhooks d' integration",
  titreEn: "Integration webhooks",
  description: "Notification sortante vers un systeme externe.",
  descriptionEn: "Outbound notification to an external system.",
  aide: "Evenement, URL et secret definissent la livraison.",
  aideEn: "Event, URL and secret define delivery.",
  lister: (params) => api.lister("admtd-integration-webhooks", params),
  creer: (data) => api.creer("admtd-integration-webhooks", data),
  modifier: (id, data) => api.modifier("admtd-integration-webhooks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("tenant", "Tenant", "Tenant"),
    col("url_cible", "URL cible", "Target URL"),
    col("evenement", "Evenement", "Event"),
    col("actif", "Actif", "Active"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    txt("url_cible", "URL cible", "Target URL"),
    txt("evenement", "Evenement", "Event"),
    chk("actif", "Actif", "Active"),
    txt("statut", "Statut", "Status"),
  ],
};

