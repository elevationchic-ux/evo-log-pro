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

export const registreAdmCSubscriptionPlan: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "subscription_plan",
  tcode: "registre-subscription-plans",
  icon: Icons.Layers,
  titre: "Plans d' abonnement",
  titreEn: "Subscription plans",
  description: "Offres tarifaires SaaS et leurs limites.",
  descriptionEn: "SaaS pricing tiers and their limits.",
  aide: "Prix, periode et quotas definissent le plan.",
  aideEn: "Price, period and quotas define the plan.",
  lister: (params) => api.lister("admc-subscription-plans", params),
  creer: (data) => api.creer("admc-subscription-plans", data),
  modifier: (id, data) => api.modifier("admc-subscription-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference plan", "Plan reference"),
    col("nom", "Nom", "Name"),
    col("prix_mensuel", "Prix mensuel", "Monthly price"),
    col("nb_utilisateurs", "Nb utilisateurs", "User seats"),
    col("nb_modules", "Nb modules", "Module count"),
    col("periode", "Periode", "Billing period"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference plan", "Plan reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    num("prix_mensuel", "Prix mensuel", "Monthly price"),
    num("nb_utilisateurs", "Nb utilisateurs", "User seats"),
    num("nb_modules", "Nb modules", "Module count"),
    txt("periode", "Periode", "Billing period"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmCTenantInvite: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "tenant_invite",
  tcode: "registre-tenant-invites",
  icon: Icons.UserPlus,
  titre: "Invitations des locataires",
  titreEn: "Tenant invites",
  description: "Invitation d' un utilisateur a rejoindre un tenant.",
  descriptionEn: "Invitation of a user to join a tenant.",
  aide: "Lien a echeance ; statut suit l' acceptation.",
  aideEn: "Time-limited link; status follows acceptance.",
  lister: (params) => api.lister("admc-tenant-invites", params),
  creer: (data) => api.creer("admc-tenant-invites", data),
  modifier: (id, data) => api.modifier("admc-tenant-invites", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference invitation", "Invite reference"),
    col("email", "Email", "Email"),
    col("tenant", "Tenant", "Tenant"),
    col("role_propose", "Role propose", "Proposed role"),
    col("invite_par", "Invite par", "Invited by"),
    col("date_expiration", "Expiration", "Expiry"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference invitation", "Invite reference", { requisCreation: true }),
    txt("email", "Email", "Email"),
    txt("tenant", "Tenant", "Tenant"),
    txt("role_propose", "Role propose", "Proposed role"),
    txt("invite_par", "Invite par", "Invited by"),
    dtx("date_expiration", "Expiration", "Expiry"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmCApiToken: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "api_token",
  tcode: "registre-api-tokens",
  icon: Icons.KeyRound,
  titre: "Jeton d' API",
  titreEn: "API tokens",
  description: "Credenciaux d' acces programmatique a l' API.",
  descriptionEn: "Programmatic API access credentials.",
  aide: "Portee et echeance bornent chaque jeton ; secret jamais stocke en clair.",
  aideEn: "Scope and expiry bound each token; secret never stored in clear.",
  lister: (params) => api.lister("admc-api-tokens", params),
  creer: (data) => api.creer("admc-api-tokens", data),
  modifier: (id, data) => api.modifier("admc-api-tokens", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference jeton", "Token reference"),
    col("nom", "Nom", "Name"),
    col("tenant", "Tenant", "Tenant"),
    col("portee", "Portee", "Scope"),
    col("cree_le", "Cree le", "Created"),
    col("expire_le", "Expire le", "Expires"),
    col("derniere_utilisation", "Derniere utilisation", "Last used"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference jeton", "Token reference", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("tenant", "Tenant", "Tenant"),
    txt("portee", "Portee", "Scope"),
    dtx("cree_le", "Cree le", "Created"),
    dtx("expire_le", "Expire le", "Expires"),
    dtx("derniere_utilisation", "Derniere utilisation", "Last used"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmCBillingInvoice: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "billing_invoice",
  tcode: "registre-billing-invoices",
  icon: Icons.Receipt,
  titre: "Factures d' abonnement",
  titreEn: "Billing invoices",
  description: "Facturation recurrente des abonnements SaaS.",
  descriptionEn: "Recurring billing of SaaS subscriptions.",
  aide: "Montant TTC, echeance et suivi de paiement.",
  aideEn: "Total amount, due date and payment tracking.",
  lister: (params) => api.lister("admc-billing-invoices", params),
  creer: (data) => api.creer("admc-billing-invoices", data),
  modifier: (id, data) => api.modifier("admc-billing-invoices", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference facture", "Invoice reference"),
    col("tenant", "Tenant", "Tenant"),
    col("periode_facturee", "Periode facturee", "Billed period"),
    col("montant_ht", "Montant HT", "Net amount"),
    col("tva", "TVA", "VAT"),
    col("montant_ttc", "Montant TTC", "Total amount"),
    col("date_echeance", "Echeance", "Due date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference facture", "Invoice reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    txt("periode_facturee", "Periode facturee", "Billed period"),
    num("montant_ht", "Montant HT", "Net amount"),
    num("tva", "TVA", "VAT"),
    num("montant_ttc", "Montant TTC", "Total amount"),
    dt("date_echeance", "Echeance", "Due date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreAdmCUsageMetering: ConfigRegistre = {
  permModule: "admin",
  permSousModule: "usage_metering",
  tcode: "registre-usage-metering",
  icon: Icons.Activity,
  titre: "Mesure d' usage",
  titreEn: "Usage metering",
  description: "Releve de consommation des ressources par tenant pour la facturation.",
  descriptionEn: "Per-tenant resource consumption reading for billing.",
  aide: "Unite mesuree et periode conditionnent la consommation facturable.",
  aideEn: "Measured unit and period drive billable consumption.",
  lister: (params) => api.lister("admc-usage-metering", params),
  creer: (data) => api.creer("admc-usage-metering", data),
  modifier: (id, data) => api.modifier("admc-usage-metering", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference releve", "Metering reference"),
    col("tenant", "Tenant", "Tenant"),
    col("ressource", "Ressource", "Resource"),
    col("unite", "Unite", "Unit"),
    col("quantite_consommee", "Quantite consommee", "Consumed quantity"),
    col("periode", "Periode", "Period"),
    col("date_releve", "Date releve", "Reading date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference releve", "Metering reference", { requisCreation: true }),
    txt("tenant", "Tenant", "Tenant"),
    txt("ressource", "Ressource", "Resource"),
    txt("unite", "Unite", "Unit"),
    num("quantite_consommee", "Quantite consommee", "Consumed quantity"),
    txt("periode", "Periode", "Period"),
    dtx("date_releve", "Date releve", "Reading date"),
    txt("statut", "Statut", "Status"),
  ],
};

