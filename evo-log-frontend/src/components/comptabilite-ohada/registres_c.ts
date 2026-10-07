/**
 * Configs Registre pour comptabilite-ohada (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("comptabilite-ohada");

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

export const registreCmptcJournalReversal: ConfigRegistre = {
  permModule: "comptabilite",
  permSousModule: "journal_reversal",
  tcode: "registre-journal-reversals",
  icon: Icons.History,
  titre: "Contre-passations d'ecritures",
  titreEn: "Journal reversals",
  description: "Annulation d' une ecriture comptable par une ecriture inverse.",
  descriptionEn: "Cancellation of a journal entry by an inverse entry.",
  aide: "La contre-passation reference l' ecriture annulee ; jamais de suppression.",
  aideEn: "Reversal references the cancelled entry; never delete.",
  lister: (params) => api.lister("cmptc-journal-reversals", params),
  creer: (data) => api.creer("cmptc-journal-reversals", data),
  modifier: (id, data) => api.modifier("cmptc-journal-reversals", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("ecriture_origine", "Ecriture d'origine", "Original entry"),
    col("date_reversal", "Date de contre-passation", "Reversal date"),
    col("compte_debit", "Compte debit", "Debit account"),
    col("compte_credit", "Compte credit", "Credit account"),
    col("montant", "Montant", "Amount"),
    col("motif", "Motif", "Reason"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("ecriture_origine", "Ecriture d'origine", "Original entry"),
    dt("date_reversal", "Date de contre-passation", "Reversal date"),
    txt("compte_debit", "Compte debit", "Debit account"),
    txt("compte_credit", "Compte credit", "Credit account"),
    num("montant", "Montant", "Amount"),
    txt("motif", "Motif", "Reason"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCmptcBankReconciliation: ConfigRegistre = {
  permModule: "comptabilite",
  permSousModule: "bank_reconciliation",
  tcode: "registre-bank-reconciliations",
  icon: Icons.Landmark,
  titre: "Rapprochements bancaires",
  titreEn: "Bank reconciliations",
  description: "Rapprochement entre solde comptable et releve bancaire.",
  descriptionEn: "Match between book balance and bank statement.",
  aide: "Ecart = solde comptable - solde bancaire ; points de controle justifies.",
  aideEn: "Difference = book - bank; justified control points.",
  lister: (params) => api.lister("cmptc-bank-reconciliations", params),
  creer: (data) => api.creer("cmptc-bank-reconciliations", data),
  modifier: (id, data) => api.modifier("cmptc-bank-reconciliations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference rapprochement", "Reconciliation ref"),
    col("compte_banque", "Compte bancaire", "Bank account"),
    col("date_releve", "Date releve", "Statement date"),
    col("solde_comptable", "Solde comptable", "Book balance"),
    col("solde_bancaire", "Solde bancaire", "Bank balance"),
    col("ecart", "Ecart", "Difference"),
    col("date_rapprochement", "Date rapprochement", "Reconciliation date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference rapprochement", "Reconciliation ref", { requisCreation: true }),
    txt("compte_banque", "Compte bancaire", "Bank account"),
    dt("date_releve", "Date releve", "Statement date"),
    num("solde_comptable", "Solde comptable", "Book balance"),
    num("solde_bancaire", "Solde bancaire", "Bank balance"),
    num("ecart", "Ecart", "Difference"),
    dt("date_rapprochement", "Date rapprochement", "Reconciliation date"),
    txt("statut", "Statut", "Status"),
  ],
};

