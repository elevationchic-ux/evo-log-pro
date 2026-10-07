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

export const registreB2bCContractAgreement: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "contract_agreement",
  tcode: "registre-contract-agreements",
  icon: Icons.FileSignature,
  titre: "Contrats-cadres clients",
  titreEn: "Contract agreements",
  description: "Accord commercial cadre avec un client B2B.",
  descriptionEn: "Framework commercial agreement with a B2B client.",
  aide: "Prix et echeance engages pour la duree du contrat.",
  aideEn: "Prices and terms committed for the contract duration.",
  lister: (params) => api.lister("b2bc-contracts", params),
  creer: (data) => api.creer("b2bc-contracts", data),
  modifier: (id, data) => api.modifier("b2bc-contracts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference contrat", "Contract reference"),
    col("client", "Client", "Client"),
    col("type_contrat", "Type de contrat", "Contract type"),
    col("date_debut", "Debut", "Start date"),
    col("date_fin", "Fin", "End date"),
    col("valeur_annuelle", "Valeur annuelle", "Annual value"),
    col("contact", "Contact", "Contact"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference contrat", "Contract reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("type_contrat", "Type de contrat", "Contract type"),
    dt("date_debut", "Debut", "Start date"),
    dt("date_fin", "Fin", "End date"),
    num("valeur_annuelle", "Valeur annuelle", "Annual value"),
    txt("contact", "Contact", "Contact"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreB2bCPriceList: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "price_list",
  tcode: "registre-price-lists",
  icon: Icons.Tags,
  titre: "Grilles tarifaires client",
  titreEn: "Price lists",
  description: "Tarifies negocies appliques aux commandes d' un client.",
  descriptionEn: "Negotiated rates applied to a client's orders.",
  aide: "Version et validite datent la grille.",
  aideEn: "Version and validity date the list.",
  lister: (params) => api.lister("b2bc-price-lists", params),
  creer: (data) => api.creer("b2bc-price-lists", data),
  modifier: (id, data) => api.modifier("b2bc-price-lists", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference grille", "List reference"),
    col("client", "Client", "Client"),
    col("version", "Version", "Version"),
    col("devise", "Devise", "Currency"),
    col("date_debut_validite", "Debut validite", "Valid from"),
    col("date_fin_validite", "Fin validite", "Valid to"),
    col("remise_globale_pct", "Remise globale (%)", "Global discount (%)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference grille", "List reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("version", "Version", "Version"),
    txt("devise", "Devise", "Currency"),
    dt("date_debut_validite", "Debut validite", "Valid from"),
    dt("date_fin_validite", "Fin validite", "Valid to"),
    num("remise_globale_pct", "Remise globale (%)", "Global discount (%)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreB2bCSalesOrder: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "sales_order",
  tcode: "registre-sales-orders",
  icon: Icons.ShoppingCart,
  titre: "Commandes clients",
  titreEn: "Sales orders",
  description: "Commande passee par un client B2B.",
  descriptionEn: "Order placed by a B2B client.",
  aide: "Le total engage la preparation jusqu' a la livraison.",
  aideEn: "Total commits preparation through delivery.",
  lister: (params) => api.lister("b2bc-sales-orders", params),
  creer: (data) => api.creer("b2bc-sales-orders", data),
  modifier: (id, data) => api.modifier("b2bc-sales-orders", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference commande", "Order reference"),
    col("client", "Client", "Client"),
    col("date_commande", "Date commande", "Order date"),
    col("nb_lignes", "Nombre de lignes", "Line count"),
    col("montant_total", "Montant total", "Total amount"),
    col("date_livraison_souhaitee", "Livraison souhaitee", "Requested delivery"),
    col("contrat_ref", "Contrat", "Contract"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference commande", "Order reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    dt("date_commande", "Date commande", "Order date"),
    num("nb_lignes", "Nombre de lignes", "Line count"),
    num("montant_total", "Montant total", "Total amount"),
    dt("date_livraison_souhaitee", "Livraison souhaitee", "Requested delivery"),
    txt("contrat_ref", "Contrat", "Contract"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreB2bCCreditAccount: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "credit_account",
  tcode: "registre-customer-credit-accounts",
  icon: Icons.CreditCard,
  titre: "Encours clients",
  titreEn: "Customer credit accounts",
  description: "Suivi de l'encours et de la limite de credit d' un client.",
  descriptionEn: "Tracking of a client's balance and credit limit.",
  aide: "L'encours ne doit pas depasser la limite accordee.",
  aideEn: "Balance must not exceed the granted limit.",
  lister: (params) => api.lister("b2bc-credit-accounts", params),
  creer: (data) => api.creer("b2bc-credit-accounts", data),
  modifier: (id, data) => api.modifier("b2bc-credit-accounts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference compte", "Account reference"),
    col("client", "Client", "Client"),
    col("limite_credit", "Limite de credit", "Credit limit"),
    col("encours", "Encours", "Balance"),
    col("delai_paiement_jours", "Delai de paiement (j)", "Payment terms (d)"),
    col("date_dernier_paiement", "Dernier paiement", "Last payment"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference compte", "Account reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    num("limite_credit", "Limite de credit", "Credit limit"),
    num("encours", "Encours", "Balance"),
    num("delai_paiement_jours", "Delai de paiement (j)", "Payment terms (d)"),
    dt("date_dernier_paiement", "Dernier paiement", "Last payment"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreB2bCSupportTicket: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "support_ticket",
  tcode: "registre-support-tickets",
  icon: Icons.LifeBuoy,
  titre: "Tickets support client",
  titreEn: "Support tickets",
  description: "Demande d' assistance ou reclamation d' un client B2B.",
  descriptionEn: "Assistance request or complaint from a B2B client.",
  aide: "Priorite et SLA conditionnent la prise en charge.",
  aideEn: "Priority and SLA drive handling.",
  lister: (params) => api.lister("b2bc-support-tickets", params),
  creer: (data) => api.creer("b2bc-support-tickets", data),
  modifier: (id, data) => api.modifier("b2bc-support-tickets", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference ticket", "Ticket reference"),
    col("client", "Client", "Client"),
    col("sujet", "Sujet", "Subject"),
    col("categorie", "Categorie", "Category"),
    col("priorite", "Priorite", "Priority"),
    col("date_ouverture", "Ouverture", "Opened"),
    col("date_resolution", "Resolution", "Resolved"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference ticket", "Ticket reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("sujet", "Sujet", "Subject"),
    txt("categorie", "Categorie", "Category"),
    txt("priorite", "Priorite", "Priority"),
    dtx("date_ouverture", "Ouverture", "Opened"),
    dtx("date_resolution", "Resolution", "Resolved"),
    txt("statut", "Statut", "Status"),
  ],
};

