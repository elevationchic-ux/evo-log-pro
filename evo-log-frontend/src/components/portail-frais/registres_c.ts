/**
 * Configs Registre pour portail-frais (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("portail-frais");

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

export const registreFraExpenseReport: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "expense_report",
  tcode: "registre-expense-reports",
  icon: Icons.Receipt,
  titre: "Notes de frais",
  titreEn: "Expense reports",
  description: "Note de frais consolidee soumise par le collaborateur.",
  descriptionEn: "Consolidated expense report submitted by the employee.",
  aide: "Le total et la periode encadrent la soumission.",
  aideEn: "Total and period frame the submission.",
  lister: (params) => api.lister("fra-expense-reports", params),
  creer: (data) => api.creer("fra-expense-reports", data),
  modifier: (id, data) => api.modifier("fra-expense-reports", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("periode", "Periode", "Period"),
    col("total", "Total", "Total"),
    col("nb_justificatifs", "Nb justificatifs", "Receipts"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("periode", "Periode", "Period"),
    num("total", "Total", "Total"),
    num("nb_justificatifs", "Nb justificatifs", "Receipts"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraExpenseReceipt: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "expense_receipt",
  tcode: "registre-expense-receipts",
  icon: Icons.Upload,
  titre: "Justificatifs de frais",
  titreEn: "Expense receipts",
  description: "Piece justificative rattachee a une ligne de frais.",
  descriptionEn: "Supporting document attached to an expense line.",
  aide: "La date et le montant du justificatif prouvent la depense.",
  aideEn: "The receipt date and amount prove the expense.",
  lister: (params) => api.lister("fra-expense-receipts", params),
  creer: (data) => api.creer("fra-expense-receipts", data),
  modifier: (id, data) => api.modifier("fra-expense-receipts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("note_frais", "Note de frais", "Expense report"),
    col("fournisseur", "Fournisseur", "Vendor"),
    col("montant", "Montant", "Amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("note_frais", "Note de frais", "Expense report"),
    txt("fournisseur", "Fournisseur", "Vendor"),
    num("montant", "Montant", "Amount"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraExpenseAdvance: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "expense_advance",
  tcode: "registre-expense-advances",
  icon: Icons.Wallet,
  titre: "Avances de frais",
  titreEn: "Expense advances",
  description: "Avance consentie avant la depense reelle.",
  descriptionEn: "Advance granted before the actual expense.",
  aide: "Le montant avance doit etre ensuite justifie ou rembourse.",
  aideEn: "The advance must later be justified or repaid.",
  lister: (params) => api.lister("fra-expense-advances", params),
  creer: (data) => api.creer("fra-expense-advances", data),
  modifier: (id, data) => api.modifier("fra-expense-advances", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("montant", "Montant", "Amount"),
    col("motif", "Motif", "Reason"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    num("montant", "Montant", "Amount"),
    txt("motif", "Motif", "Reason"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraPerDiemClaim: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "per_diem_claim",
  tcode: "registre-per-diem-claims",
  icon: Icons.Coins,
  titre: "Indemnites forfaitaires",
  titreEn: "Per diem claims",
  description: "Demande d' indemnite journaliere forfaitaire.",
  descriptionEn: "Daily flat-rate indemnity claim.",
  aide: "Le barme et le nombre de jours calculent l' indemnite.",
  aideEn: "The scale and days compute the indemnity.",
  lister: (params) => api.lister("fra-per-diem-claims", params),
  creer: (data) => api.creer("fra-per-diem-claims", data),
  modifier: (id, data) => api.modifier("fra-per-diem-claims", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("jours", "Jours", "Days"),
    col("taux_journalier", "Taux journalier", "Daily rate"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    num("jours", "Jours", "Days"),
    num("taux_journalier", "Taux journalier", "Daily rate"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraMileageClaim: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "mileage_claim",
  tcode: "registre-mileage-claims",
  icon: Icons.Gauge,
  titre: "Frais kilometriques",
  titreEn: "Mileage claims",
  description: "Indemnisation de deplacements en vehicule personnel.",
  descriptionEn: "Reimbursement of personal-vehicle travel.",
  aide: "La distance x le bareme justifie le montant.",
  aideEn: "Distance times the rate justifies the amount.",
  lister: (params) => api.lister("fra-mileage-claims", params),
  creer: (data) => api.creer("fra-mileage-claims", data),
  modifier: (id, data) => api.modifier("fra-mileage-claims", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("km", "Kilometres", "Kilometers"),
    col("trajet", "Trajet", "Route"),
    col("montant", "Montant", "Amount"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    num("km", "Kilometres", "Kilometers"),
    txt("trajet", "Trajet", "Route"),
    num("montant", "Montant", "Amount"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraMealExpense: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "meal_expense",
  tcode: "registre-meal-expenses",
  icon: Icons.Coffee,
  titre: "Frais de restauration",
  titreEn: "Meal expenses",
  description: "Repis professionnels engages et justifies.",
  descriptionEn: "Professional meals incurred and justified.",
  aide: "Les participants et le motif professionnel conditionnent l' acceptation.",
  aideEn: "Attendees and business purpose condition acceptance.",
  lister: (params) => api.lister("fra-meal-expenses", params),
  creer: (data) => api.creer("fra-meal-expenses", data),
  modifier: (id, data) => api.modifier("fra-meal-expenses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("montant", "Montant", "Amount"),
    col("nb_personnes", "Nb personnes", "People"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    num("montant", "Montant", "Amount"),
    num("nb_personnes", "Nb personnes", "People"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraTravelBooking: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "travel_booking",
  tcode: "registre-travel-bookings",
  icon: Icons.Plane,
  titre: "Reservations de deplacement",
  titreEn: "Travel bookings",
  description: "Reservation de transport pour un deplacement professionnel.",
  descriptionEn: "Transport booking for a business trip.",
  aide: "Le respect de la politique voyage limite le cout.",
  aideEn: "Travel-policy compliance caps the cost.",
  lister: (params) => api.lister("fra-travel-bookings", params),
  creer: (data) => api.creer("fra-travel-bookings", data),
  modifier: (id, data) => api.modifier("fra-travel-bookings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("mode", "Mode", "Mode"),
    col("destination", "Destination", "Destination"),
    col("date_depart", "Depart", "Departure"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("mode", "Mode", "Mode"),
    txt("destination", "Destination", "Destination"),
    dt("date_depart", "Depart", "Departure"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraHotelStay: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "hotel_stay",
  tcode: "registre-hotel-stays",
  icon: Icons.BedDouble,
  titre: "Nuits d' hotel",
  titreEn: "Hotel stays",
  description: "Hebergement hotelier lie a un deplacement.",
  descriptionEn: "Hotel lodging tied to a trip.",
  aide: "Le nombre de nuits et le tarif nuit encadrent la depense.",
  aideEn: "Nights and nightly rate bound the expense.",
  lister: (params) => api.lister("fra-hotel-stays", params),
  creer: (data) => api.creer("fra-hotel-stays", data),
  modifier: (id, data) => api.modifier("fra-hotel-stays", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("hotel", "Hotel", "Hotel"),
    col("nuits", "Nuits", "Nights"),
    col("montant", "Montant", "Amount"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("hotel", "Hotel", "Hotel"),
    num("nuits", "Nuits", "Nights"),
    num("montant", "Montant", "Amount"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraTransportExpense: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "transport_expense",
  tcode: "registre-transport-expenses",
  icon: Icons.Car,
  titre: "Frais de transport local",
  titreEn: "Transport expenses",
  description: "Taxi, VTC, péage et transports locaux.",
  descriptionEn: "Taxi, ride-hailing, tolls and local transport.",
  aide: "Le motif et le trajet prouvent le caractere professionnel.",
  aideEn: "Purpose and route prove the business nature.",
  lister: (params) => api.lister("fra-transport-expenses", params),
  creer: (data) => api.creer("fra-transport-expenses", data),
  modifier: (id, data) => api.modifier("fra-transport-expenses", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("type", "Type", "Type"),
    col("montant", "Montant", "Amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("type", "Type", "Type"),
    num("montant", "Montant", "Amount"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraClientEntertainment: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "client_entertainment",
  tcode: "registre-client-entertainment",
  icon: Icons.Users,
  titre: "Frais de representation client",
  titreEn: "Client entertainment",
  description: "Depenses d' reception liees a un client.",
  descriptionEn: "Hospitality expenses tied to a client.",
  aide: "Le client recu et le business purpose encadrent la depense.",
  aideEn: "The hosted client and business purpose bound the expense.",
  lister: (params) => api.lister("fra-client-entertainment", params),
  creer: (data) => api.creer("fra-client-entertainment", data),
  modifier: (id, data) => api.modifier("fra-client-entertainment", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("client", "Client", "Client"),
    col("montant", "Montant", "Amount"),
    col("nb_invites", "Nb invites", "Guests"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("client", "Client", "Client"),
    num("montant", "Montant", "Amount"),
    num("nb_invites", "Nb invites", "Guests"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraConferenceFee: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "conference_fee",
  tcode: "registre-conference-fees",
  icon: Icons.BookOpen,
  titre: "Frais de salon et conference",
  titreEn: "Conference fees",
  description: "Inscription et frais lies a un evenement professionnel.",
  descriptionEn: "Registration and costs tied to a professional event.",
  aide: "L' evenement et le role (participant/exposant) justifient la depense.",
  aideEn: "The event and role (attendee/exhibitor) justify the expense.",
  lister: (params) => api.lister("fra-conference-fees", params),
  creer: (data) => api.creer("fra-conference-fees", data),
  modifier: (id, data) => api.modifier("fra-conference-fees", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("collaborateur", "Collaborateur", "Employee"),
    col("evenement", "Evenement", "Event"),
    col("montant", "Montant", "Amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("collaborateur", "Collaborateur", "Employee"),
    txt("evenement", "Evenement", "Event"),
    num("montant", "Montant", "Amount"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraOfficeSupply: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "office_supply",
  tcode: "registre-office-supplies",
  icon: Icons.Boxes,
  titre: "Achats de fournitures",
  titreEn: "Office supplies",
  description: "Achat de petites fournitures pour le service.",
  descriptionEn: "Purchase of minor supplies for the department.",
  aide: "Le centre de cout et le bon de commande encadrent l' achat.",
  aideEn: "The cost center and purchase order bound the buy.",
  lister: (params) => api.lister("fra-office-supplies", params),
  creer: (data) => api.creer("fra-office-supplies", data),
  modifier: (id, data) => api.modifier("fra-office-supplies", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("demandeur", "Demandeur", "Requester"),
    col("article", "Article", "Item"),
    col("montant", "Montant", "Amount"),
    col("centre_cout", "Centre de cout", "Cost center"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("demandeur", "Demandeur", "Requester"),
    txt("article", "Article", "Item"),
    num("montant", "Montant", "Amount"),
    txt("centre_cout", "Centre de cout", "Cost center"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraCardTransaction: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "card_transaction",
  tcode: "registre-card-transactions",
  icon: Icons.CreditCard,
  titre: "Transactions carte entreprise",
  titreEn: "Card transactions",
  description: "Paiement effectue avec la carte de l' entreprise.",
  descriptionEn: "Payment made with the company card.",
  aide: "Le rapprochement transaction / justificatif clot la carte.",
  aideEn: "Matching transaction to receipt closes the card.",
  lister: (params) => api.lister("fra-card-transactions", params),
  creer: (data) => api.creer("fra-card-transactions", data),
  modifier: (id, data) => api.modifier("fra-card-transactions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("titulaire", "Titulaire", "Holder"),
    col("marchand", "Marchand", "Merchant"),
    col("montant", "Montant", "Amount"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("titulaire", "Titulaire", "Holder"),
    txt("marchand", "Marchand", "Merchant"),
    num("montant", "Montant", "Amount"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraCurrencyConversion: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "currency_conversion",
  tcode: "registre-currency-conversions",
  icon: Icons.Percent,
  titre: "Conversions de devise",
  titreEn: "Currency conversions",
  description: "Conversion d' un frais en devise vers la devise de remboursement.",
  descriptionEn: "Conversion of a foreign-currency expense to reimbursement currency.",
  aide: "Le taux applique et la date figent la conversion.",
  aideEn: "The applied rate and date freeze the conversion.",
  lister: (params) => api.lister("fra-currency-conversions", params),
  creer: (data) => api.creer("fra-currency-conversions", data),
  modifier: (id, data) => api.modifier("fra-currency-conversions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("frais", "Frais", "Expense"),
    col("devise_source", "Devise source", "Source currency"),
    col("montant_source", "Montant source", "Source amount"),
    col("taux", "Taux", "Rate"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("frais", "Frais", "Expense"),
    txt("devise_source", "Devise source", "Source currency"),
    num("montant_source", "Montant source", "Source amount"),
    num("taux", "Taux", "Rate"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraExpenseApproval: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "expense_approval",
  tcode: "registre-expense-approvals",
  icon: Icons.CheckCircle2,
  titre: "Validations de frais",
  titreEn: "Expense approvals",
  description: "Validation hiérarchique d' une note de frais.",
  descriptionEn: "Managerial approval of an expense report.",
  aide: "Le valideur et la date attestent le controle N+1.",
  aideEn: "The approver and date evidence the N+1 control.",
  lister: (params) => api.lister("fra-expense-approvals", params),
  creer: (data) => api.creer("fra-expense-approvals", data),
  modifier: (id, data) => api.modifier("fra-expense-approvals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("note_frais", "Note de frais", "Expense report"),
    col("valideur", "Validateur", "Approver"),
    col("commentaire", "Commentaire", "Comment"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("note_frais", "Note de frais", "Expense report"),
    txt("valideur", "Validateur", "Approver"),
    txt("commentaire", "Commentaire", "Comment"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraExpenseDispute: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "expense_dispute",
  tcode: "registre-expense-disputes",
  icon: Icons.XCircle,
  titre: "Litiges de frais",
  titreEn: "Expense disputes",
  description: "Contestation d' un refus ou d' un montant de frais.",
  descriptionEn: "Challenge of an expense rejection or amount.",
  aide: "Le motif du litige et la piece jointe relancent l' examen.",
  aideEn: "The dispute reason and attachment reopen the review.",
  lister: (params) => api.lister("fra-expense-disputes", params),
  creer: (data) => api.creer("fra-expense-disputes", data),
  modifier: (id, data) => api.modifier("fra-expense-disputes", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("note_frais", "Note de frais", "Expense report"),
    col("motif", "Motif", "Reason"),
    col("montant_conteste", "Montant conteste", "Disputed amount"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("note_frais", "Note de frais", "Expense report"),
    txt("motif", "Motif", "Reason"),
    num("montant_conteste", "Montant conteste", "Disputed amount"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraVatRecovery: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "vat_recovery",
  tcode: "registre-vat-recovery",
  icon: Icons.Landmark,
  titre: "Recuperation TVA sur frais",
  titreEn: "VAT recovery",
  description: "Identification de la TVA recuperable sur une depense.",
  descriptionEn: "Identification of recoverable VAT on an expense.",
  aide: "La mention TVA sur la facture conditionne la recuperation.",
  aideEn: "The VAT line on the invoice conditions recovery.",
  lister: (params) => api.lister("fra-vat-recovery", params),
  creer: (data) => api.creer("fra-vat-recovery", data),
  modifier: (id, data) => api.modifier("fra-vat-recovery", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("frais", "Frais", "Expense"),
    col("montant_ht", "Montant HT", "Net amount"),
    col("tva", "TVA", "VAT"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("frais", "Frais", "Expense"),
    num("montant_ht", "Montant HT", "Net amount"),
    num("tva", "TVA", "VAT"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraExpenseBudgetTracking: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "expense_budget_tracking",
  tcode: "registre-expense-budget-tracking",
  icon: Icons.TrendingUp,
  titre: "Suivi budget de frais",
  titreEn: "Expense budget tracking",
  description: "Comparaison budget alloue / frais engages par centre de cout.",
  descriptionEn: "Comparison of allocated budget vs incurred expense per cost center.",
  aide: "Le depassement du budget declenche l' alerte.",
  aideEn: "Exceeding budget triggers the alert.",
  lister: (params) => api.lister("fra-expense-budget-tracking", params),
  creer: (data) => api.creer("fra-expense-budget-tracking", data),
  modifier: (id, data) => api.modifier("fra-expense-budget-tracking", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("centre_cout", "Centre de cout", "Cost center"),
    col("periode", "Periode", "Period"),
    col("budget", "Budget", "Budget"),
    col("engage", "Engage", "Committed"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("centre_cout", "Centre de cout", "Cost center"),
    txt("periode", "Periode", "Period"),
    num("budget", "Budget", "Budget"),
    num("engage", "Engage", "Committed"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFraExpenseCategory: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "expense_category",
  tcode: "registre-expense-categories",
  icon: Icons.ListChecks,
  titre: "Categories de frais",
  titreEn: "Expense categories",
  description: "Referentiel des categories de frais autorisees.",
  descriptionEn: "Reference of allowed expense categories.",
  aide: "Le plafond par categorie encadre la saisie.",
  aideEn: "The per-category cap frames entry.",
  lister: (params) => api.lister("fra-expense-categories", params),
  creer: (data) => api.creer("fra-expense-categories", data),
  modifier: (id, data) => api.modifier("fra-expense-categories", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("libelle", "Libelle", "Label"),
    col("plafond", "Plafond", "Cap"),
    col("justificatif_requis", "Justificatif requis", "Receipt required"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("libelle", "Libelle", "Label"),
    num("plafond", "Plafond", "Cap"),
    chk("justificatif_requis", "Justificatif requis", "Receipt required"),
    txt("statut", "Statut", "Status"),
  ],
};

