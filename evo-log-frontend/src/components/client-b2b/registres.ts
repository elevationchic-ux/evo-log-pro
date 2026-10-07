/**
 * Configs Registre pour client-b2b (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("client-b2b");

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

export const registreClientOnboarding: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "client_onboarding",
  tcode: "registre-client-onboarding",
  icon: Icons.UserPlus,
  titre: "Admission nouveau client",
  titreEn: "New client onboarding",
  description: "Dossier admission / KYC.",
  descriptionEn: "Admission / KYC file.",
  aide: "Piece legale et referentiel bancaire obligatoires.",
  aideEn: "Legal paper and bank reference mandatory.",
  lister: (params) => api.lister("client-onboardings", params),
  creer: (data) => api.creer("client-onboardings", data),
  modifier: (id, data) => api.modifier("client-onboardings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("raison_sociale", "Raison sociale", "Legal name"),
    col("niu", "NIU", "Tax ID"),
    col("rc", "Registre commerce", "Reg. commerce"),
    col("contact_principal", "Contact", "Contact"),
    col("email", "Email", "Email"),
    col("telephone", "Telephone", "Phone"),
    col("date_demande", "Demande", "Request"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    txt("raison_sociale", "Raison sociale", "Legal name"),
    txt("niu", "NIU", "Tax ID"),
    txt("rc", "Registre commerce", "Reg. commerce"),
    txt("contact_principal", "Contact", "Contact"),
    txt("email", "Email", "Email"),
    txt("telephone", "Telephone", "Phone"),
    dt("date_demande", "Demande", "Request"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSlaContract: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "sla_management",
  tcode: "registre-sla-management",
  icon: Icons.Timer,
  titre: "Niveau de service / penalisations",
  titreEn: "SLA / penalties",
  description: "Engagement service et mesures.",
  descriptionEn: "Service commitments and measures.",
  aide: "Penalite si 2 mois consecutifs sous seuil.",
  aideEn: "Penalty if 2 months under threshold.",
  lister: (params) => api.lister("sla-contracts", params),
  creer: (data) => api.creer("sla-contracts", data),
  modifier: (id, data) => api.modifier("sla-contracts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("type_prestation", "Type prestation", "Service type"),
    col("engagement_valeur", "Valeur engagement", "Committed value"),
    col("taux_atteint_pct", "Taux atteint %", "Achieved %"),
    col("penalite_xaf", "Penalite XAF", "Penalty XAF"),
    col("periode", "Periode", "Period"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    txt("type_prestation", "Type prestation", "Service type"),
    num("engagement_valeur", "Valeur engagement", "Committed value"),
    num("taux_atteint_pct", "Taux atteint %", "Achieved %"),
    num("penalite_xaf", "Penalite XAF", "Penalty XAF"),
    txt("periode", "Periode", "Period"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreB2bContract: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "contract_tracking",
  tcode: "registre-contract-tracking",
  icon: Icons.FileSignature,
  titre: "Contrats cadres / avenants",
  titreEn: "Framework contracts / amendments",
  description: "Contrats long terme clients.",
  descriptionEn: "Long-term client contracts.",
  aide: "Chaque avenant est versionne.",
  aideEn: "Each amendment versioned.",
  lister: (params) => api.lister("b2b-contracts", params),
  creer: (data) => api.creer("b2b-contracts", data),
  modifier: (id, data) => api.modifier("b2b-contracts", id, data),
  unicite: "numero_contrat",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_contrat", "Numero contrat", "Contract number", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("type_contrat", "Type", "Type"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("montant_engage_xaf", "Montant engage", "Committed amount"),
    col("nb_avenants", "Nb avenants", "Amendments"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_contrat", "Numero contrat", "Contract number", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    sel("type_contrat", "Type", "Type", "type_contrat"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    num("montant_engage_xaf", "Montant engage", "Committed amount"),
    num("nb_avenants", "Nb avenants", "Amendments"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreSatisfactionSurvey: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "satisfaction_survey",
  tcode: "registre-satisfaction-surveys",
  icon: Icons.Smile,
  titre: "Enquetes satisfaction NPS",
  titreEn: "Satisfaction / NPS surveys",
  description: "Enquetes periodiques clients.",
  descriptionEn: "Periodic client surveys.",
  aide: "Score NPS 9-10 vs 0-6.",
  aideEn: "NPS score 9-10 vs 0-6.",
  lister: (params) => api.lister("satisfaction-surveys", params),
  creer: (data) => api.creer("satisfaction-surveys", data),
  modifier: (id, data) => api.modifier("satisfaction-surveys", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("date_enquete", "Date", "Survey date"),
    col("note_global", "Note globale", "Overall score"),
    col("score_nps", "Score NPS", "NPS score"),
    col("commentaires", "Commentaires", "Comments"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    dt("date_enquete", "Date", "Survey date"),
    num("note_global", "Note globale", "Overall score"),
    num("score_nps", "Score NPS", "NPS score"),
    txt("commentaires", "Commentaires", "Comments"),
  ],
};


export const registreClientCreditLimit: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "credit_limit",
  tcode: "registre-credit-limits",
  icon: Icons.CreditCard,
  titre: "Plafonds de credit client",
  titreEn: "Client credit limits",
  description: "Encours autorise par client.",
  descriptionEn: "Authorized outstanding per client.",
  aide: "Blocage commandes si depassement.",
  aideEn: "Order block if exceeded.",
  lister: (params) => api.lister("client-credit-limits", params),
  creer: (data) => api.creer("client-credit-limits", data),
  modifier: (id, data) => api.modifier("client-credit-limits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("plafond_xaf", "Plafond", "Limit"),
    col("encours_actuel_xaf", "Encours", "Current outstanding"),
    col("delai_paiement_jours", "Delai paiement (j)", "Payment terms (d)"),
    col("date_revision", "Revision", "Review"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    num("plafond_xaf", "Plafond", "Limit"),
    num("encours_actuel_xaf", "Encours", "Current outstanding"),
    num("delai_paiement_jours", "Delai paiement (j)", "Payment terms (d)"),
    dt("date_revision", "Revision", "Review"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreB2bDocument: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "document_exchange",
  tcode: "registre-document-exchange",
  icon: Icons.FolderOpen,
  titre: "Echange documents contractuels",
  titreEn: "Contract document exchange",
  description: "Echanges pieces contractuelles.",
  descriptionEn: "Contract document exchanges.",
  aide: "Accuse reception obligatoire.",
  aideEn: "Receipt ack required.",
  lister: (params) => api.lister("b2b-documents", params),
  creer: (data) => api.creer("b2b-documents", data),
  modifier: (id, data) => api.modifier("b2b-documents", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("type_document", "Type document", "Document type"),
    col("nom_fichier", "Nom fichier", "File name"),
    col("date_envoi", "Envoi", "Send date"),
    col("date_reception", "Reception", "Receipt date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    txt("type_document", "Type document", "Document type"),
    txt("nom_fichier", "Nom fichier", "File name"),
    dtx("date_envoi", "Envoi", "Send date"),
    dtx("date_reception", "Reception", "Receipt date"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreServiceRequest: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "service_request",
  tcode: "registre-service-requests",
  icon: Icons.Inbox,
  titre: "Demandes de service client",
  titreEn: "Client service requests",
  description: "Tickets et demandes clients.",
  descriptionEn: "Client tickets / requests.",
  aide: "SLA reponse contractuel.",
  aideEn: "Contractual response SLA.",
  lister: (params) => api.lister("service-requests", params),
  creer: (data) => api.creer("service-requests", data),
  modifier: (id, data) => api.modifier("service-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("type_demande", "Type demande", "Request type"),
    col("description", "Description", "Description"),
    col("date_creation", "Creation", "Creation date"),
    col("date_echeance", "Echeance", "Due date"),
    col("priorite", "Priorite", "Priority"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    txt("type_demande", "Type demande", "Request type"),
    txt("description", "Description", "Description"),
    dtx("date_creation", "Creation", "Creation date"),
    dtx("date_echeance", "Echeance", "Due date"),
    sel("priorite", "Priorite", "Priority", "priorite"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registrePricingAgreement: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "pricing_agreement",
  tcode: "registre-pricing-agreements",
  icon: Icons.Tag,
  titre: "Accords tarifaires / remises",
  titreEn: "Pricing agreements / discounts",
  description: "Grille tarifaire par client.",
  descriptionEn: "Pricing grid per client.",
  aide: "Revue annuelle commerciale.",
  aideEn: "Annual sales review.",
  lister: (params) => api.lister("pricing-agreements", params),
  creer: (data) => api.creer("pricing-agreements", data),
  modifier: (id, data) => api.modifier("pricing-agreements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("type_prestation", "Type prestation", "Service type"),
    col("remise_pct", "Remise %", "Discount %"),
    col("palier_volume", "Palier volume", "Volume tier"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    txt("type_prestation", "Type prestation", "Service type"),
    num("remise_pct", "Remise %", "Discount %"),
    txt("palier_volume", "Palier volume", "Volume tier"),
    dt("date_debut", "Debut", "Start"),
    dt("date_fin", "Fin", "End"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreShipmentBooking: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "shipment_booking",
  tcode: "registre-shipment-booking",
  icon: Icons.CalendarCheck,
  titre: "Reservation expedition client",
  titreEn: "Shipment booking",
  description: "Reservation creneau quai ou navire.",
  descriptionEn: "Berth / vessel slot reservation.",
  aide: "Confirmation 48h avant.",
  aideEn: "Confirmation 48h before.",
  lister: (params) => api.lister("shipment-bookings", params),
  creer: (data) => api.creer("shipment-bookings", data),
  modifier: (id, data) => api.modifier("shipment-bookings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("escale_id", "Escale", "Call"),
    col("type_expedition", "Type expedition", "Shipment type"),
    col("date_reservation", "Reservation", "Booking date"),
    col("date_prevue", "Prevue", "Planned date"),
    col("conteneurs_prevus", "Conteneurs prevus", "Expected containers"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    num("escale_id", "Escale", "Call"),
    sel("type_expedition", "Type expedition", "Shipment type", "type_expedition"),
    dtx("date_reservation", "Reservation", "Booking date"),
    dtx("date_prevue", "Prevue", "Planned date"),
    num("conteneurs_prevus", "Conteneurs prevus", "Expected containers"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreClientClaim: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "claim_dispute",
  tcode: "registre-claim-dispute",
  icon: Icons.AlertOctagon,
  titre: "Reclamation / litige client",
  titreEn: "Client claim / dispute",
  description: "Dossier litige commercial.",
  descriptionEn: "Commercial dispute file.",
  aide: "Escalade juridique apres 30j.",
  aideEn: "Legal escalation after 30 days.",
  lister: (params) => api.lister("client-claims", params),
  creer: (data) => api.creer("client-claims", data),
  modifier: (id, data) => api.modifier("client-claims", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("objet", "Objet", "Subject"),
    col("description", "Description", "Description"),
    col("date_reclamation", "Reclamation", "Complaint date"),
    col("montant_reclame_xaf", "Montant reclame", "Amount claimed"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    txt("objet", "Objet", "Subject"),
    txt("description", "Description", "Description"),
    dt("date_reclamation", "Reclamation", "Complaint date"),
    num("montant_reclame_xaf", "Montant reclame", "Amount claimed"),
    sel("statut", "Statut", "Status", "statut"),
  ],
};


export const registreAccountReport: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "account_report",
  tcode: "registre-account-reports",
  icon: Icons.FileBarChart,
  titre: "Releves periodiques compte client",
  titreEn: "Client account statements",
  description: "Releves et balances envoyes.",
  descriptionEn: "Statements and balances sent.",
  aide: "Approbation client = lettrage.",
  aideEn: "Client approval = reconciliation.",
  lister: (params) => api.lister("account-reports", params),
  creer: (data) => api.creer("account-reports", data),
  modifier: (id, data) => api.modifier("account-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference", { searchable: true }),
    col("client_id", "Client", "Client"),
    col("periode_debut", "Debut", "Start"),
    col("periode_fin", "Fin", "End"),
    col("factures_emises_xaf", "Factures emis", "Invoices issued"),
    col("reglements_recus_xaf", "Reglements recus", "Payments received"),
    col("solde_a_payer_xaf", "Solde a payer", "Balance owed"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { obligatoire: true }),
    num("client_id", "Client", "Client"),
    dt("periode_debut", "Debut", "Start"),
    dt("periode_fin", "Fin", "End"),
    num("factures_emises_xaf", "Factures emis", "Invoices issued"),
    num("reglements_recus_xaf", "Reglements recus", "Payments received"),
    num("solde_a_payer_xaf", "Solde a payer", "Balance owed"),
  ],
};

