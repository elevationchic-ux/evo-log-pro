/**
 * Configs Registre pour dashboard (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("dashboard");

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

export const registreModuleHealth: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "module_health",
  tcode: "registre-module-health",
  icon: Icons.HeartPulse,
  titre: "Sante fonctionnelle des modules",
  titreEn: "Module functional health",
  description: "Etat de marche par module.",
  descriptionEn: "Working state per module.",
  aide: "Refresh toutes les 15 min.",
  aideEn: "Refresh every 15 min.",
  lister: (params) => api.lister("module-healths", params),
  creer: (data) => api.creer("module-healths", data),
  modifier: (id, data) => api.modifier("module-healths", id, data),
  unicite: "code_module",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_module", "Code module", "Module code"),
    col("etat", "Etat", "State"),
    col("nombre_requetes_jour", "Nb requetes / jour", "Daily calls"),
    col("taux_erreur_pct", "Taux erreur %", "Error rate %"),
    col("latence_p95_ms", "Latence p95 (ms)", "Latency p95 (ms)"),
    col("dernier_incident", "Dernier incident", "Last incident"),
  ],
  champs: [
    txt("code_module", "Code module", "Module code", { requisCreation: true }),
    sel("etat", "Etat", "State", "etat"),
    num("nombre_requetes_jour", "Nb requetes / jour", "Daily calls"),
    num("taux_erreur_pct", "Taux erreur %", "Error rate %"),
    num("latence_p95_ms", "Latence p95 (ms)", "Latency p95 (ms)"),
    dtx("dernier_incident", "Dernier incident", "Last incident"),
  ],
};


export const registreActivityRecord: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "activity_feed",
  tcode: "registre-activity-feed",
  icon: Icons.History,
  titre: "Flux d'activite recent",
  titreEn: "Recent activity feed",
  description: "Timeline multi-module.",
  descriptionEn: "Cross-module timeline.",
  aide: "Visible seulement par utilisateur concerne.",
  aideEn: "Only visible to concerned user.",
  lister: (params) => api.lister("activity-records", params),
  creer: (data) => api.creer("activity-records", data),
  modifier: (id, data) => api.modifier("activity-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("module_source", "Module source", "Source module"),
    col("type_action", "Type action", "Action type"),
    col("utilisateur", "Utilisateur", "User"),
    col("entite", "Entite", "Entity"),
    col("horodatage", "Horodatage", "Timestamp"),
    col("resume", "Resume", "Summary"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("module_source", "Module source", "Source module"),
    txt("type_action", "Type action", "Action type"),
    txt("utilisateur", "Utilisateur", "User"),
    txt("entite", "Entite", "Entity"),
    dtx("horodatage", "Horodatage", "Timestamp"),
    txt("resume", "Resume", "Summary"),
  ],
};


export const registreUnifiedTask: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "task_center",
  tcode: "registre-task-center",
  icon: Icons.CheckSquare,
  titre: "Centre de taches / to-do unifie",
  titreEn: "Unified task center",
  description: "Taches transverses par utilisateur.",
  descriptionEn: "Cross-module tasks per user.",
  aide: "Chaque tache pointe vers objet metier.",
  aideEn: "Each task points to a business object.",
  lister: (params) => api.lister("unified-tasks", params),
  creer: (data) => api.creer("unified-tasks", data),
  modifier: (id, data) => api.modifier("unified-tasks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("titre", "Titre", "Title"),
    col("module_source", "Module source", "Source module"),
    col("entite_id", "ID entite", "Entity id"),
    col("assigne_a", "Assigne a", "Assigned to"),
    col("date_echeance", "Echeance", "Due date"),
    col("priorite", "Priorite", "Priority"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("titre", "Titre", "Title"),
    txt("module_source", "Module source", "Source module"),
    num("entite_id", "ID entite", "Entity id"),
    num("assigne_a", "Assigne a", "Assigned to"),
    dtx("date_echeance", "Echeance", "Due date"),
    sel("priorite", "Priorite", "Priority", "priorite"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreQuickAction: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "quick_actions",
  tcode: "registre-quick-actions",
  icon: Icons.Zap,
  titre: "Raccourcis operationnels config.",
  titreEn: "Configurable operational shortcuts",
  description: "Actions favorites lancees depuis dashboard.",
  descriptionEn: "Favorite actions from dashboard.",
  aide: "Par user.",
  aideEn: "Per user.",
  lister: (params) => api.lister("quick-actions", params),
  creer: (data) => api.creer("quick-actions", data),
  modifier: (id, data) => api.modifier("quick-actions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("libelle", "Libelle", "Label"),
    col("module_source", "Module source", "Source module"),
    col("url_action", "URL action", "Action URL"),
    col("utilisateur_id", "Utilisateur", "User"),
    col("ordre", "Ordre", "Order"),
    col("actif", "Actif", "Active"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("libelle", "Libelle", "Label"),
    txt("module_source", "Module source", "Source module"),
    txt("url_action", "URL action", "Action URL"),
    num("utilisateur_id", "Utilisateur", "User"),
    num("ordre", "Ordre", "Order"),
    chk("actif", "Actif", "Active"),
  ],
};


export const registreTeamPerformance: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "team_performance",
  tcode: "registre-team-performance",
  icon: Icons.Users,
  titre: "Performance et productivite equipes",
  titreEn: "Team performance and productivity",
  description: "KPI collectifs par equipe.",
  descriptionEn: "Team KPIs.",
  aide: "Revu par manager N+1.",
  aideEn: "Reviewed by N+1 manager.",
  lister: (params) => api.lister("team-performances", params),
  creer: (data) => api.creer("team-performances", data),
  modifier: (id, data) => api.modifier("team-performances", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("equipe", "Equipe", "Team"),
    col("periode", "Periode", "Period"),
    col("objectifs_atteints_pct", "Objectifs atteints %", "Goals reached %"),
    col("volume_traite", "Volume traite", "Processed volume"),
    col("qualite_score", "Score qualite", "Quality score"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("equipe", "Equipe", "Team"),
    txt("periode", "Periode", "Period"),
    num("objectifs_atteints_pct", "Objectifs atteints %", "Goals reached %"),
    num("volume_traite", "Volume traite", "Processed volume"),
    num("qualite_score", "Score qualite", "Quality score"),
  ],
};


export const registreFinancialSummary: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "financial_summary",
  tcode: "registre-financial-summary",
  icon: Icons.CircleDollarSign,
  titre: "Synthese financiere consolidee",
  titreEn: "Consolidated financial summary",
  description: "CA, marge, BFR, tresorerie.",
  descriptionEn: "Revenue, margin, WC, cash.",
  aide: "Update mensuelle.",
  aideEn: "Monthly update.",
  lister: (params) => api.lister("financial-summaries", params),
  creer: (data) => api.creer("financial-summaries", data),
  modifier: (id, data) => api.modifier("financial-summaries", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("periode", "Periode", "Period"),
    col("ca_consolide_xaf", "CA consolide", "Consolidated revenue"),
    col("marge_brute_xaf", "Marge brute", "Gross margin"),
    col("ebitda_xaf", "EBITDA", "EBITDA"),
    col("bfr_xaf", "BFR", "Working capital"),
    col("tresorerie_xaf", "Tresorerie", "Cash"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("periode", "Periode", "Period"),
    num("ca_consolide_xaf", "CA consolide", "Consolidated revenue"),
    num("marge_brute_xaf", "Marge brute", "Gross margin"),
    num("ebitda_xaf", "EBITDA", "EBITDA"),
    num("bfr_xaf", "BFR", "Working capital"),
    num("tresorerie_xaf", "Tresorerie", "Cash"),
  ],
};


export const registreOperationalAlert: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "operational_alerts",
  tcode: "registre-operational-alerts",
  icon: Icons.AlertOctagon,
  titre: "Alertes operationnelles croisees",
  titreEn: "Cross-operational alerts",
  description: "Signaux critiques multi-modules.",
  descriptionEn: "Cross-module critical signals.",
  aide: "Escalade hierarchique automatique.",
  aideEn: "Automatic hierarchical escalation.",
  lister: (params) => api.lister("operational-alerts", params),
  creer: (data) => api.creer("operational-alerts", data),
  modifier: (id, data) => api.modifier("operational-alerts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("module_source", "Module source", "Source module"),
    col("niveau", "Niveau", "Level"),
    col("description", "Description", "Description"),
    col("date_alerte", "Date", "Date"),
    col("destinataire", "Destinataire", "Recipient"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("module_source", "Module source", "Source module"),
    sel("niveau", "Niveau", "Level", "niveau"),
    txt("description", "Description", "Description"),
    dtx("date_alerte", "Date", "Date"),
    txt("destinataire", "Destinataire", "Recipient"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreRecentDocument: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "document_center",
  tcode: "registre-document-center",
  icon: Icons.FolderOpen,
  titre: "Centre documents recents / partages",
  titreEn: "Recent and shared documents",
  description: "Documents accessibles par utilisateur.",
  descriptionEn: "User-accessible documents.",
  aide: "Permission heritee de la ligne metier.",
  aideEn: "Inherited permission from business line.",
  lister: (params) => api.lister("recent-documents", params),
  creer: (data) => api.creer("recent-documents", data),
  modifier: (id, data) => api.modifier("recent-documents", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("titre", "Titre", "Title"),
    col("module_source", "Module source", "Source module"),
    col("entite_id", "ID entite", "Entity id"),
    col("url", "URL", "URL"),
    col("date_creation", "Creation", "Creation"),
    col("partage", "Partage", "Sharing"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("titre", "Titre", "Title"),
    txt("module_source", "Module source", "Source module"),
    num("entite_id", "ID entite", "Entity id"),
    txt("url", "URL", "URL"),
    dtx("date_creation", "Creation", "Creation"),
    sel("partage", "Partage", "Sharing", "partage"),
  ],
};


export const registreUnifiedAgenda: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "calendar_agenda",
  tcode: "registre-calendar-agenda",
  icon: Icons.Calendar,
  titre: "Agenda consolide multi-module",
  titreEn: "Cross-module consolidated agenda",
  description: "Rendez-vous, echeances, evenements.",
  descriptionEn: "Meetings, deadlines, events.",
  aide: "Export ICS disponible.",
  aideEn: "ICS export available.",
  lister: (params) => api.lister("unified-agenda", params),
  creer: (data) => api.creer("unified-agenda", data),
  modifier: (id, data) => api.modifier("unified-agenda", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("titre", "Titre", "Title"),
    col("module_source", "Module source", "Source module"),
    col("entite_id", "ID entite", "Entity id"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("invite_par", "Invite par", "Invited by"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("titre", "Titre", "Title"),
    txt("module_source", "Module source", "Source module"),
    num("entite_id", "ID entite", "Entity id"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    txt("invite_par", "Invite par", "Invited by"),
  ],
};


export const registreIntegrationStatus: ConfigRegistre = {
  permModule: "dashboard",
  permSousModule: "integration_status",
  tcode: "registre-integration-status",
  icon: Icons.Link2,
  titre: "Etat integrations externes",
  titreEn: "External integrations status",
  description: "Sonde etat des APIs tierces.",
  descriptionEn: "Probe third-party APIs.",
  aide: "Alerte si 3 echecs consecutifs.",
  aideEn: "Alert if 3 consecutive failures.",
  lister: (params) => api.lister("integration-statuses", params),
  creer: (data) => api.creer("integration-statuses", data),
  modifier: (id, data) => api.modifier("integration-statuses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("nom_integration", "Nom integration", "Integration name"),
    col("url_testee", "URL testee", "Tested URL"),
    col("date_dernier_test", "Dernier test", "Last test"),
    col("succes", "Succes", "Success"),
    col("latence_ms", "Latence (ms)", "Latency (ms)"),
    col("message_erreur", "Message erreur", "Error message"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("nom_integration", "Nom integration", "Integration name"),
    txt("url_testee", "URL testee", "Tested URL"),
    dtx("date_dernier_test", "Dernier test", "Last test"),
    chk("succes", "Succes", "Success"),
    num("latence_ms", "Latence (ms)", "Latency (ms)"),
    txt("message_erreur", "Message erreur", "Error message"),
  ],
};

