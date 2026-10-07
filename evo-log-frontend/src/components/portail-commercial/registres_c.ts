/**
 * Configs Registre pour portail-commercial (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-commercial");

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

export const registreCommLead: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "lead",
  tcode: "registre-leads",
  icon: Icons.UserPlus,
  titre: "Pistes commerciales",
  titreEn: "Leads",
  description: "Contact potentiel identifie par le commercial.",
  descriptionEn: "Potential contact identified by the salesperson.",
  aide: "La source et la qualification pilotent le suivi.",
  aideEn: "Source and qualification drive the follow-up.",
  lister: (params) => api.lister("comm-leads", params),
  creer: (data) => api.creer("comm-leads", data),
  modifier: (id, data) => api.modifier("comm-leads", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prospect", "Prospect", "Prospect"),
    col("source", "Source", "Source"),
    col("segment", "Segment", "Segment"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prospect", "Prospect", "Prospect"),
    txt("source", "Source", "Source"),
    txt("segment", "Segment", "Segment"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommOpportunity: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "opportunity",
  tcode: "registre-opportunities",
  icon: Icons.Target,
  titre: " opportunites",
  titreEn: "Opportunities",
  description: "Occasion de vente suivie en pipeline par le commercial.",
  descriptionEn: "Sales opportunity tracked in the pipeline.",
  aide: "Le montant et la phase estiment la probalite de gain.",
  aideEn: "Amount and stage estimate the win probability.",
  lister: (params) => api.lister("comm-opportunities", params),
  creer: (data) => api.creer("comm-opportunities", data),
  modifier: (id, data) => api.modifier("comm-opportunities", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("libelle", "Libelle", "Title"),
    col("montant_estime", "Montant estime", "Estimated amount"),
    col("cloture_prevue", "Cloture prevue", "Expected close"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("libelle", "Libelle", "Title"),
    num("montant_estime", "Montant estime", "Estimated amount"),
    dt("cloture_prevue", "Cloture prevue", "Expected close"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommQuote: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "quote",
  tcode: "registre-quotes",
  icon: Icons.FileText,
  titre: "Devis",
  titreEn: "Quotes",
  description: "Proposition commerciale chiffree emise pour un client.",
  descriptionEn: "Priced commercial proposal issued to a client.",
  aide: "La validite borne la duree de l' offre.",
  aideEn: "Validity bounds the offer duration.",
  lister: (params) => api.lister("comm-quotes", params),
  creer: (data) => api.creer("comm-quotes", data),
  modifier: (id, data) => api.modifier("comm-quotes", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("montant", "Montant", "Amount"),
    col("validite", "Validite", "Validity"),
    col("date_emission", "Emission", "Issued"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    num("montant", "Montant", "Amount"),
    dt("validite", "Validite", "Validity"),
    dt("date_emission", "Emission", "Issued"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommSalesOrder: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "sales_order",
  tcode: "registre-sales-orders",
  icon: Icons.ShoppingCart,
  titre: "Commandes clients",
  titreEn: "Sales orders",
  description: "Commande fermee passe par le client via le commercial.",
  descriptionEn: "Firmed order placed by the client via the salesperson.",
  aide: "La confirmation de commande engage la livraison.",
  aideEn: "The order confirmation commits delivery.",
  lister: (params) => api.lister("comm-sales-orders", params),
  creer: (data) => api.creer("comm-sales-orders", data),
  modifier: (id, data) => api.modifier("comm-sales-orders", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("devis", "Devis", "Quote"),
    col("montant", "Montant", "Amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("devis", "Devis", "Quote"),
    num("montant", "Montant", "Amount"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommCustomerVisit: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "customer_visit",
  tcode: "registre-customer-visits",
  icon: Icons.MapPinned,
  titre: "Visites clients",
  titreEn: "Customer visits",
  description: "Compte-rendu d' une visite chez un client.",
  descriptionEn: "Report of a visit to a client.",
  aide: "L' objectif et le resultat structurent la relation.",
  aideEn: "The objective and outcome structure the relationship.",
  lister: (params) => api.lister("comm-customer-visits", params),
  creer: (data) => api.creer("comm-customer-visits", data),
  modifier: (id, data) => api.modifier("comm-customer-visits", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("date", "Date", "Date"),
    col("interlocuteur", "Interlocuteur", "Contact"),
    col("compte_rendu", "Compte-rendu", "Report"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    dtx("date", "Date", "Date"),
    txt("interlocuteur", "Interlocuteur", "Contact"),
    txt("compte_rendu", "Compte-rendu", "Report"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommSampleRequest: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "sample_request",
  tcode: "registre-samples-requests",
  icon: Icons.Boxes,
  titre: "Demandes d' echantillons",
  titreEn: "Sample requests",
  description: "Demande d' envoi d' un echantillon a un prospect/client.",
  descriptionEn: "Request to send a sample to a prospect/client.",
  aide: "La quantite et le destinataire preparent l' envoi.",
  aideEn: "Quantity and recipient prepare the shipment.",
  lister: (params) => api.lister("comm-samples-requests", params),
  creer: (data) => api.creer("comm-samples-requests", data),
  modifier: (id, data) => api.modifier("comm-samples-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("produit", "Produit", "Product"),
    col("quantite", "Quantite", "Quantity"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("produit", "Produit", "Product"),
    num("quantite", "Quantite", "Quantity"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommTender: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "tender",
  tcode: "registre-tenders",
  icon: Icons.Newspaper,
  titre: "Appels d' offres",
  titreEn: "Tenders",
  description: "Reponse a un appel d' offres public ou prive.",
  descriptionEn: "Response to a public or private tender.",
  aide: "La date limite et le depot engagent la candidature.",
  aideEn: "The deadline and filing commit the bid.",
  lister: (params) => api.lister("comm-tenders", params),
  creer: (data) => api.creer("comm-tenders", data),
  modifier: (id, data) => api.modifier("comm-tenders", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("acheteur", "Acheteur", "Buyer"),
    col("objet", "Objet", "Object"),
    col("date_limite", "Date limite", "Deadline"),
    col("montant_offre", "Montant offre", "Bid amount"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("acheteur", "Acheteur", "Buyer"),
    txt("objet", "Objet", "Object"),
    dt("date_limite", "Date limite", "Deadline"),
    num("montant_offre", "Montant offre", "Bid amount"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommContractRenewal: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "contract_renewal",
  tcode: "registre-contract-renewals",
  icon: Icons.FileSignature,
  titre: "Renouvellements de contrat",
  titreEn: "Contract renewals",
  description: "Suivi du renouvellement d' un contrat client.",
  descriptionEn: "Tracking of a client contract renewal.",
  aide: "L' echeance et la valeur engageent l' anticipation.",
  aideEn: "The due date and value drive the anticipation.",
  lister: (params) => api.lister("comm-contract-renewals", params),
  creer: (data) => api.creer("comm-contract-renewals", data),
  modifier: (id, data) => api.modifier("comm-contract-renewals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("contrat", "Contrat", "Contract"),
    col("echeance", "Echeance", "Due date"),
    col("valeur", "Valeur", "Value"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("contrat", "Contrat", "Contract"),
    dt("echeance", "Echeance", "Due date"),
    num("valeur", "Valeur", "Value"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommPriceRequest: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "price_request",
  tcode: "registre-price-requests",
  icon: Icons.CircleDollarSign,
  titre: "Demandes de prix",
  titreEn: "Price requests",
  description: "Demande de tarification specifique d' un client.",
  descriptionEn: "Request for a client's specific pricing.",
  aide: "La remise accordee est justifiee par le volume.",
  aideEn: "The granted discount is justified by volume.",
  lister: (params) => api.lister("comm-price-requests", params),
  creer: (data) => api.creer("comm-price-requests", data),
  modifier: (id, data) => api.modifier("comm-price-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("produit", "Produit", "Product"),
    col("remise", "Remise (%)", "Discount (%)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("produit", "Produit", "Product"),
    num("remise", "Remise (%)", "Discount (%)"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommCreditRequest: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "credit_request",
  tcode: "registre-credit-requests",
  icon: Icons.CreditCard,
  titre: "Demandes d' encours client",
  titreEn: "Credit requests",
  description: "Demande d' augmentation de la ligne de credit d' un client.",
  descriptionEn: "Request to raise a client's credit line.",
  aide: "Le montant sollicite doit rester coherent avec le risque.",
  aideEn: "The requested amount must stay consistent with risk.",
  lister: (params) => api.lister("comm-credit-requests", params),
  creer: (data) => api.creer("comm-credit-requests", data),
  modifier: (id, data) => api.modifier("comm-credit-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("encours_actuel", "Encours actuel", "Current limit"),
    col("montant_souhaite", "Montant souhaite", "Desired amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    num("encours_actuel", "Encours actuel", "Current limit"),
    num("montant_souhaite", "Montant souhaite", "Desired amount"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommOrderModification: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "order_modification",
  tcode: "registre-order-modifications",
  icon: Icons.GitBranch,
  titre: "Modifications de commande",
  titreEn: "Order modifications",
  description: "Avenant demande par le client sur une commande confirmee.",
  descriptionEn: "Change requested by the client on a confirmed order.",
  aide: "Toute modification apres confirmation est tracee et justifiee.",
  aideEn: "Any post-confirmation change is traced and justified.",
  lister: (params) => api.lister("comm-order-modifications", params),
  creer: (data) => api.creer("comm-order-modifications", data),
  modifier: (id, data) => api.modifier("comm-order-modifications", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("commande", "Commande", "Order"),
    col("changement", "Changement", "Change"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("commande", "Commande", "Order"),
    txt("changement", "Changement", "Change"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommCustomerComplaint: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "customer_complaint",
  tcode: "registre-customer-complaints",
  icon: Icons.MessageSquare,
  titre: "Reclamations clients",
  titreEn: "Customer complaints",
  description: "Reclamation exprimee par un client via son commercial.",
  descriptionEn: "Complaint raised by a client via the salesperson.",
  aide: "Le delai de traitement mesure la qualite de service.",
  aideEn: "The handling time measures service quality.",
  lister: (params) => api.lister("comm-customer-complaints", params),
  creer: (data) => api.creer("comm-customer-complaints", data),
  modifier: (id, data) => api.modifier("comm-customer-complaints", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("objet", "Objet", "Subject"),
    col("canal", "Canal", "Channel"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("objet", "Objet", "Subject"),
    txt("canal", "Canal", "Channel"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommUpsellRecord: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "upsell_record",
  tcode: "registre-upsell-records",
  icon: Icons.TrendingUp,
  titre: "Actions de vente additionnelle",
  titreEn: "Upsell records",
  description: "Opportunite de vente supplementaire sur un compte existant.",
  descriptionEn: "Additional sales opportunity on an existing account.",
  aide: "Le potentiel identifie alimente le chiffre d' affaires.",
  aideEn: "The identified potential feeds revenue.",
  lister: (params) => api.lister("comm-upsell-records", params),
  creer: (data) => api.creer("comm-upsell-records", data),
  modifier: (id, data) => api.modifier("comm-upsell-records", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("offre", "Offre", "Offer"),
    col("montant_potentiel", "Montant potentiel", "Potential amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("offre", "Offre", "Offer"),
    num("montant_potentiel", "Montant potentiel", "Potential amount"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommCommissionStatement: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "commission_statement",
  tcode: "registre-commission-statements",
  icon: Icons.Percent,
  titre: "Etats de commission",
  titreEn: "Commission statements",
  description: "Calcul de la commission due au commercial sur ses ventes.",
  descriptionEn: "Calculation of the commission owed to the salesperson.",
  aide: "Le taux applique aux ventes valide conditionne la commission.",
  aideEn: "The rate applied to validated sales conditions the commission.",
  lister: (params) => api.lister("comm-commission-statements", params),
  creer: (data) => api.creer("comm-commission-statements", data),
  modifier: (id, data) => api.modifier("comm-commission-statements", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("commercial", "Commercial", "Salesperson"),
    col("periode", "Periode", "Period"),
    col("base_vente", "Base de vente", "Sales base"),
    col("taux", "Taux (%)", "Rate (%)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("commercial", "Commercial", "Salesperson"),
    txt("periode", "Periode", "Period"),
    num("base_vente", "Base de vente", "Sales base"),
    num("taux", "Taux (%)", "Rate (%)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCommPipelineReview: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "pipeline_review",
  tcode: "registre-pipeline-reviews",
  icon: Icons.LineChart,
  titre: "Revues de pipeline",
  titreEn: "Pipeline reviews",
  description: "Revue periodique du pipeline commercial d' un representant.",
  descriptionEn: "Periodic review of a rep's sales pipeline.",
  aide: "La valeur ponderee projette le chiffre d' affaires futur.",
  aideEn: "The weighted value projects future revenue.",
  lister: (params) => api.lister("comm-pipeline-reviews", params),
  creer: (data) => api.creer("comm-pipeline-reviews", data),
  modifier: (id, data) => api.modifier("comm-pipeline-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("commercial", "Commercial", "Salesperson"),
    col("nb_opportunites", "Nb opportunites", "Opportunities"),
    col("valeur_ponderee", "Valeur ponderee", "Weighted value"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("commercial", "Commercial", "Salesperson"),
    num("nb_opportunites", "Nb opportunites", "Opportunities"),
    num("valeur_ponderee", "Valeur ponderee", "Weighted value"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

