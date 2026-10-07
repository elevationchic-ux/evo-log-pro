/**
 * Configs Registre pour annuaire-prestataires (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("annuaire-prestataires");

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

export const registreProvProfile: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_profile",
  tcode: "registre-provider-profiles",
  icon: Icons.Building2,
  titre: "Fiches prestataires",
  titreEn: "Provider profiles",
  description: "Fiche d' identite d' un prestataire / sous-traitant.",
  descriptionEn: "Identity record of a provider / subcontractor.",
  aide: "Le type de prestation et la zone definissent le champs d' action.",
  aideEn: "Service type and zone define the scope.",
  lister: (params) => api.lister("prov-provider-profiles", params),
  creer: (data) => api.creer("prov-provider-profiles", data),
  modifier: (id, data) => api.modifier("prov-provider-profiles", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("raison_sociale", "Raison sociale", "Company name"),
    col("type_prestation", "Type de prestation", "Service type"),
    col("zone", "Zone", "Zone"),
    col("contact", "Contact", "Contact"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("raison_sociale", "Raison sociale", "Company name"),
    txt("type_prestation", "Type de prestation", "Service type"),
    txt("zone", "Zone", "Zone"),
    txt("contact", "Contact", "Contact"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvCategory: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_category",
  tcode: "registre-provider-categories",
  icon: Icons.Tags,
  titre: "Categories de prestataires",
  titreEn: "Provider categories",
  description: "Classification des prestataires par metier.",
  descriptionEn: "Classification of providers by trade.",
  aide: "La categorie pilote le workflow de qualification.",
  aideEn: "The category drives the qualification workflow.",
  lister: (params) => api.lister("prov-provider-categories", params),
  creer: (data) => api.creer("prov-provider-categories", data),
  modifier: (id, data) => api.modifier("prov-provider-categories", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("libelle", "Libelle", "Label"),
    col("exigence_documentaire", "Exigence documentaire", "Doc requirement"),
    col("nb_prestataires", "Nb prestataires", "Providers"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("libelle", "Libelle", "Label"),
    chk("exigence_documentaire", "Exigence documentaire", "Doc requirement"),
    num("nb_prestataires", "Nb prestataires", "Providers"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvCertification: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_certification",
  tcode: "registre-provider-certifications",
  icon: Icons.Award,
  titre: "Certifications prestataires",
  titreEn: "Provider certifications",
  description: "Certification / agrement detenu par un prestataire.",
  descriptionEn: "Certification / accreditation held by a provider.",
  aide: "La validite de la certification conditionne la mise en service.",
  aideEn: "Certification validity conditions deployment.",
  lister: (params) => api.lister("prov-provider-certifications", params),
  creer: (data) => api.creer("prov-provider-certifications", data),
  modifier: (id, data) => api.modifier("prov-provider-certifications", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("intitule", "Intitule", "Title"),
    col("emetteur", "Emetteur", "Issuer"),
    col("expire_le", "Expire le", "Expires"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("intitule", "Intitule", "Title"),
    txt("emetteur", "Emetteur", "Issuer"),
    dt("expire_le", "Expire le", "Expires"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvInsuranceAttestation: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "insurance_attestation",
  tcode: "registre-insurance-attestations",
  icon: Icons.ShieldCheck,
  titre: "Attestations d' assurance",
  titreEn: "Insurance attestations",
  description: "Attestation d' assurance RC / caution d' un prestataire.",
  descriptionEn: "Liability insurance / bond attestation of a provider.",
  aide: "Le montant couvert et la date limite encadrent l' assurance.",
  aideEn: "Covered amount and deadline bound the insurance.",
  lister: (params) => api.lister("prov-insurance-attestations", params),
  creer: (data) => api.creer("prov-insurance-attestations", data),
  modifier: (id, data) => api.modifier("prov-insurance-attestations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("type_assurance", "Type", "Insurance type"),
    col("montant_couvert", "Montant couvert", "Covered amount"),
    col("expire_le", "Expire le", "Expires"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("type_assurance", "Type", "Insurance type"),
    num("montant_couvert", "Montant couvert", "Covered amount"),
    dt("expire_le", "Expire le", "Expires"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvServiceContract: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "service_contract",
  tcode: "registre-service-contracts",
  icon: Icons.FileSignature,
  titre: "Contrats de prestation",
  titreEn: "Service contracts",
  description: "Contrat cadre ou ponctuel lie a un prestataire.",
  descriptionEn: "Framework or one-off contract with a provider.",
  aide: "La duree et le montant engagent la relation.",
  aideEn: "Duration and amount commit the relationship.",
  lister: (params) => api.lister("prov-service-contracts", params),
  creer: (data) => api.creer("prov-service-contracts", data),
  modifier: (id, data) => api.modifier("prov-service-contracts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("objet", "Objet", "Object"),
    col("montant", "Montant", "Amount"),
    col("echeance", "Echeance", "End date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("objet", "Objet", "Object"),
    num("montant", "Montant", "Amount"),
    dt("echeance", "Echeance", "End date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvEvaluation: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_evaluation",
  tcode: "registre-provider-evaluations",
  icon: Icons.Star,
  titre: "Evaluations de prestataires",
  titreEn: "Provider evaluations",
  description: "Scoring periodique d' un prestataire sur des criteres.",
  descriptionEn: "Periodic scoring of a provider on criteria.",
  aide: "Le score global conditionne le renouvellement.",
  aideEn: "The overall score conditions renewal.",
  lister: (params) => api.lister("prov-provider-evaluations", params),
  creer: (data) => api.creer("prov-provider-evaluations", data),
  modifier: (id, data) => api.modifier("prov-provider-evaluations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("periode", "Periode", "Period"),
    col("score", "Score", "Score"),
    col("evalueur", "Evaluateur", "Evaluator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("periode", "Periode", "Period"),
    num("score", "Score", "Score"),
    txt("evalueur", "Evaluateur", "Evaluator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvIncident: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_incident",
  tcode: "registre-provider-incidents",
  icon: Icons.AlertTriangle,
  titre: "Incidents prestataires",
  titreEn: "Provider incidents",
  description: "Manquement ou incident impute a un prestataire.",
  descriptionEn: "Breach or incident attributed to a provider.",
  aide: "La gravite alimente la notation et la mise en demeure.",
  aideEn: "Severity feeds the scoring and the formal notice.",
  lister: (params) => api.lister("prov-provider-incidents", params),
  creer: (data) => api.creer("prov-provider-incidents", data),
  modifier: (id, data) => api.modifier("prov-provider-incidents", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("description", "Description", "Description"),
    col("gravite", "Gravite", "Severity"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("description", "Description", "Description"),
    txt("gravite", "Gravite", "Severity"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvAvailabilityCalendar: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "availability_calendar",
  tcode: "registre-availability-calendars",
  icon: Icons.CalendarDays,
  titre: "Calendriers de disponibilite",
  titreEn: "Availability calendars",
  description: "Disponible declaree par un prestataire pour une periode.",
  descriptionEn: "Availability declared by a provider for a period.",
  aide: "Le taux de disponibilite oriente l' affectation des missions.",
  aideEn: "The availability rate guides mission assignment.",
  lister: (params) => api.lister("prov-availability-calendars", params),
  creer: (data) => api.creer("prov-availability-calendars", data),
  modifier: (id, data) => api.modifier("prov-availability-calendars", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("semaine", "Semaine", "Week"),
    col("creneaux_libres", "Creneaux libres", "Free slots"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("semaine", "Semaine", "Week"),
    num("creneaux_libres", "Creneaux libres", "Free slots"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvPriceList: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "price_list",
  tcode: "registre-price-lists",
  icon: Icons.CircleDollarSign,
  titre: "Grilles tarifaires prestataires",
  titreEn: "Provider price lists",
  description: "Barime de prix propose par un prestataire.",
  descriptionEn: "Rate card offered by a provider.",
  aide: "La date d' application et la validite encadrent le tarif.",
  aideEn: "Application date and validity bound the rate.",
  lister: (params) => api.lister("prov-price-lists", params),
  creer: (data) => api.creer("prov-price-lists", data),
  modifier: (id, data) => api.modifier("prov-price-lists", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("unite_prix", "Prix unitaire", "Unit price"),
    col("validite", "Validite", "Validity"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    num("unite_prix", "Prix unitaire", "Unit price"),
    dt("validite", "Validite", "Validity"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvContact: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_contact",
  tcode: "registre-provider-contacts",
  icon: Icons.Contact,
  titre: "Contacts prestataires",
  titreEn: "Provider contacts",
  description: "Interlocuteur designe chez un prestataire.",
  descriptionEn: "Designated contact person at a provider.",
  aide: "Le role (commercial / exploitation) structure la relation.",
  aideEn: "The role (sales / ops) structures the relationship.",
  lister: (params) => api.lister("prov-provider-contacts", params),
  creer: (data) => api.creer("prov-provider-contacts", data),
  modifier: (id, data) => api.modifier("prov-provider-contacts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("nom", "Nom", "Name"),
    col("role", "Role", "Role"),
    col("telephone", "Telephone", "Phone"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("nom", "Nom", "Name"),
    txt("role", "Role", "Role"),
    txt("telephone", "Telephone", "Phone"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvOnboarding: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_onboarding",
  tcode: "registre-provider-onboarding",
  icon: Icons.UserCheck,
  titre: "Onboarding prestataires",
  titreEn: "Provider onboarding",
  description: "Parcours de référencement d' un nouveau prestataire.",
  descriptionEn: "Onboarding path of a newly referenced provider.",
  aide: "La complete des pieces conditionne la mise en service.",
  aideEn: "Document completeness conditions go-live.",
  lister: (params) => api.lister("prov-provider-onboarding", params),
  creer: (data) => api.creer("prov-provider-onboarding", data),
  modifier: (id, data) => api.modifier("prov-provider-onboarding", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("etapes_faites", "Etapes faites", "Steps done"),
    col("etapes_total", "Etapes", "Total steps"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    num("etapes_faites", "Etapes faites", "Steps done"),
    num("etapes_total", "Etapes", "Total steps"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvReview: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_review",
  tcode: "registre-provider-reviews",
  icon: Icons.MessageSquare,
  titre: "Avis sur prestataires",
  titreEn: "Provider reviews",
  description: "Retour qualitatif libre apres une prestation.",
  descriptionEn: "Free qualitative feedback after a service.",
  aide: "L' avis vient completer le score formel.",
  aideEn: "The review complements the formal score.",
  lister: (params) => api.lister("prov-provider-reviews", params),
  creer: (data) => api.creer("prov-provider-reviews", data),
  modifier: (id, data) => api.modifier("prov-provider-reviews", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("commentaire", "Commentaire", "Comment"),
    col("nb_etoiles", "Nb etoiles", "Stars"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("commentaire", "Commentaire", "Comment"),
    num("nb_etoiles", "Nb etoiles", "Stars"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvRfqRequest: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "rfq_request",
  tcode: "registre-rfq-requests",
  icon: Icons.FileText,
  titre: "Demandes de devis",
  titreEn: "RFQ requests",
  description: "Consultation prix lancee aupres de plusieurs prestataires.",
  descriptionEn: "Price consultation launched with several providers.",
  aide: "Les offres recues comparent pour selectionner.",
  aideEn: "Received bids are compared to select.",
  lister: (params) => api.lister("prov-rfq-requests", params),
  creer: (data) => api.creer("prov-rfq-requests", data),
  modifier: (id, data) => api.modifier("prov-rfq-requests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("objet", "Objet", "Object"),
    col("nb_offres", "Nb offres", "Bids"),
    col("date_limite", "Date limite", "Deadline"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("objet", "Objet", "Object"),
    num("nb_offres", "Nb offres", "Bids"),
    dt("date_limite", "Date limite", "Deadline"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvIntervention: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_intervention",
  tcode: "registre-provider-interventions",
  icon: Icons.Wrench,
  titre: "Interventions prestataires",
  titreEn: "Provider interventions",
  description: "Mission realisee par un prestataire sur site.",
  descriptionEn: "Mission carried out by a provider on site.",
  aide: "Le compte-rendu d' intervention atteste le service fait.",
  aideEn: "The intervention report evidences the service done.",
  lister: (params) => api.lister("prov-provider-interventions", params),
  creer: (data) => api.creer("prov-provider-interventions", data),
  modifier: (id, data) => api.modifier("prov-provider-interventions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("site", "Site", "Site"),
    col("date", "Date", "Date"),
    col("compte_rendu", "Compte-rendu", "Report"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("site", "Site", "Site"),
    dtx("date", "Date", "Date"),
    txt("compte_rendu", "Compte-rendu", "Report"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvComplianceDoc: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "compliance_document",
  tcode: "registre-compliance-documents",
  icon: Icons.FileBadge,
  titre: "Documents de conformite",
  titreEn: "Compliance documents",
  description: "Piece de conformite exigee d' un prestataire (Kbis, reglement...).",
  descriptionEn: "Compliance document required from a provider.",
  aide: "La validite de la piece conditionne la reference.",
  aideEn: "Document validity conditions the reference status.",
  lister: (params) => api.lister("prov-compliance-documents", params),
  creer: (data) => api.creer("prov-compliance-documents", data),
  modifier: (id, data) => api.modifier("prov-compliance-documents", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("type_piece", "Type", "Doc type"),
    col("expire_le", "Expire le", "Expires"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("type_piece", "Type", "Doc type"),
    dt("expire_le", "Expire le", "Expires"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvBankDetail: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_bank_detail",
  tcode: "registre-provider-bank-details",
  icon: Icons.Landmark,
  titre: "Coordonnees bancaires prestataires",
  titreEn: "Provider bank details",
  description: "RIB du prestataire pour le reglement des factures.",
  descriptionEn: "Provider bank account for invoice settlement.",
  aide: "Un IBAN verifie evite le paiement vers un compte erroné.",
  aideEn: "A verified IBAN prevents payment to a wrong account.",
  lister: (params) => api.lister("prov-provider-bank-details", params),
  creer: (data) => api.creer("prov-provider-bank-details", data),
  modifier: (id, data) => api.modifier("prov-provider-bank-details", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("banque", "Banque", "Bank"),
    col("iban_verifie", "IBAN verifie", "IBAN verified"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("banque", "Banque", "Bank"),
    chk("iban_verifie", "IBAN verifie", "IBAN verified"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreProvBlacklist: ConfigRegistre = {
  permModule: "transport",
  permSousModule: "provider_blacklist",
  tcode: "registre-provider-blacklist",
  icon: Icons.Ban,
  titre: "Exclusions de prestataires",
  titreEn: "Provider blacklist",
  description: "Mise a l' index / exclusion d' un prestataire.",
  descriptionEn: "Blacklisting / exclusion of a provider.",
  aide: "Le motif et la duree justifient la mise a l' index.",
  aideEn: "The reason and duration justify the blacklisting.",
  lister: (params) => api.lister("prov-provider-blacklist", params),
  creer: (data) => api.creer("prov-provider-blacklist", data),
  modifier: (id, data) => api.modifier("prov-provider-blacklist", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("prestataire", "Prestataire", "Provider"),
    col("motif", "Motif", "Reason"),
    col("debut", "Debut", "Start"),
    col("fin_prevue", "Fin prevue", "Planned end"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("prestataire", "Prestataire", "Provider"),
    txt("motif", "Motif", "Reason"),
    dt("debut", "Debut", "Start"),
    dt("fin_prevue", "Fin prevue", "Planned end"),
    txt("statut", "Statut", "Status"),
  ],
};

