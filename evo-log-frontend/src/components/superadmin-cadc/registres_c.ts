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

export const registreSaCAuditLogReview: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "audit_log_review",
  tcode: "registre-audit-log-reviews",
  icon: Icons.ScrollText,
  titre: "Revues des journaux d' audit",
  titreEn: "Audit log reviews",
  description: "Examen periodique des journaux d' activite sensible.",
  descriptionEn: "Periodic review of sensitive activity logs.",
  aide: "Chaque revue consigne un verdict et un perimetre.",
  aideEn: "Each review records a verdict and a scope.",
  lister: (params) => api.lister("sac-audit-log-reviews", params),
  creer: (data) => api.creer("sac-audit-log-reviews", data),
  modifier: (id, data) => api.modifier("sac-audit-log-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference revue", "Review reference"),
    col("perimetre", "Perimetre", "Scope"),
    col("date_debut", "Debut", "From"),
    col("date_fin", "Fin", "To"),
    col("evenements_examines", "Evenements examines", "Events reviewed"),
    col("reviewer", "Reviewer", "Reviewer"),
    col("verdict", "Verdict", "Verdict"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference revue", "Review reference", { requisCreation: true }),
    txt("perimetre", "Perimetre", "Scope"),
    dtx("date_debut", "Debut", "From"),
    dtx("date_fin", "Fin", "To"),
    num("evenements_examines", "Evenements examines", "Events reviewed"),
    txt("reviewer", "Reviewer", "Reviewer"),
    txt("verdict", "Verdict", "Verdict"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreSaCSystemParameter: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "system_parameter",
  tcode: "registre-system-parameters",
  icon: Icons.Settings,
  titre: "Parametres systeme",
  titreEn: "System parameters",
  description: "Reglage global de la plateforme (valeur cle/parametre).",
  descriptionEn: "Global platform setting (key/value).",
  aide: "Toute modification est tracable et reversible.",
  aideEn: "Any change is traceable and reversible.",
  lister: (params) => api.lister("sac-system-parameters", params),
  creer: (data) => api.creer("sac-system-parameters", data),
  modifier: (id, data) => api.modifier("sac-system-parameters", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Cle du parametre", "Parameter key"),
    col("valeur", "Valeur", "Value"),
    col("categorie", "Categorie", "Category"),
    col("portee", "Portee", "Scope"),
    col("modifie_par", "Modifie par", "Modified by"),
    col("date_modification", "Date modification", "Modified at"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Cle du parametre", "Parameter key", { requisCreation: true }),
    txt("valeur", "Valeur", "Value"),
    txt("categorie", "Categorie", "Category"),
    txt("portee", "Portee", "Scope"),
    txt("modifie_par", "Modifie par", "Modified by"),
    dtx("date_modification", "Date modification", "Modified at"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreSaCPlatformAlert: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "platform_alert",
  tcode: "registre-platform-alerts",
  icon: Icons.BellRing,
  titre: "Alertes plateforme",
  titreEn: "Platform alerts",
  description: "Notification d' un incident ou depassement de seuile technique.",
  descriptionEn: "Notification of a technical incident or threshold breach.",
  aide: "Severite et acquittement structurent la reponse.",
  aideEn: "Severity and acknowledgement structure the response.",
  lister: (params) => api.lister("sac-platform-alerts", params),
  creer: (data) => api.creer("sac-platform-alerts", data),
  modifier: (id, data) => api.modifier("sac-platform-alerts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference alerte", "Alert reference"),
    col("titre", "Titre", "Title"),
    col("source", "Source", "Source"),
    col("severite", "Severite", "Severity"),
    col("date_detection", "Detection", "Detected at"),
    col("acquitte_par", "Acquitte par", "Acknowledged by"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference alerte", "Alert reference", { requisCreation: true }),
    txt("titre", "Titre", "Title"),
    txt("source", "Source", "Source"),
    txt("severite", "Severite", "Severity"),
    dtx("date_detection", "Detection", "Detected at"),
    txt("acquitte_par", "Acquitte par", "Acknowledged by"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreSaCMigrationRun: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "migration_run",
  tcode: "registre-migration-runs",
  icon: Icons.GitBranch,
  titre: "Executions de migration",
  titreEn: "Migration runs",
  description: "Journal des deploiements de migrations base de donnees.",
  descriptionEn: "Log of database migration deployments.",
  aide: "Reversible ; statut et duree consignes a chaque run.",
  aideEn: "Reversible; status and duration logged per run.",
  lister: (params) => api.lister("sac-migration-runs", params),
  creer: (data) => api.creer("sac-migration-runs", data),
  modifier: (id, data) => api.modifier("sac-migration-runs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference run", "Run reference"),
    col("revision", "Revision", "Revision"),
    col("environnement", "Environnement", "Environment"),
    col("lance_par", "Lance par", "Launched by"),
    col("date_debut", "Debut", "Start"),
    col("duree_sec", "Duree (s)", "Duration (s)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference run", "Run reference", { requisCreation: true }),
    txt("revision", "Revision", "Revision"),
    txt("environnement", "Environnement", "Environment"),
    txt("lance_par", "Lance par", "Launched by"),
    dtx("date_debut", "Debut", "Start"),
    num("duree_sec", "Duree (s)", "Duration (s)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreSaCLicenseKey: ConfigRegistre = {
  permModule: "superadmin",
  permSousModule: "license_key",
  tcode: "registre-license-keys",
  icon: Icons.Key,
  titre: "Cles de licence",
  titreEn: "License keys",
  description: "Cles de licence produit et leur activation.",
  descriptionEn: "Product license keys and their activation.",
  aide: "Une cle a un etat et un titulaire identifies.",
  aideEn: "A key has an identified state and holder.",
  lister: (params) => api.lister("sac-license-keys", params),
  creer: (data) => api.creer("sac-license-keys", data),
  modifier: (id, data) => api.modifier("sac-license-keys", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference cle", "Key reference"),
    col("produit", "Produit", "Product"),
    col("titulaire", "Titulaire", "Holder"),
    col("sieges_licencies", "Sieges licencies", "Licensed seats"),
    col("date_activation", "Activation", "Activation date"),
    col("date_expiration", "Expiration", "Expiry date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference cle", "Key reference", { requisCreation: true }),
    txt("produit", "Produit", "Product"),
    txt("titulaire", "Titulaire", "Holder"),
    num("sieges_licencies", "Sieges licencies", "Licensed seats"),
    dt("date_activation", "Activation", "Activation date"),
    dt("date_expiration", "Expiration", "Expiry date"),
    txt("statut", "Statut", "Status"),
  ],
};

