/**
 * Configs Registre pour finance-ohada (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("finance-ohada");

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

export const registreFincCashFlowForecast: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "cash_flow_forecast",
  tcode: "registre-cash-flow-forecasts",
  icon: Icons.TrendingUp,
  titre: "Previsions de tresorerie",
  titreEn: "Cash flow forecasts",
  description: "Projection des entrees et sorties de tresorerie par periode.",
  descriptionEn: "Projection of treasury inflows and outflows by period.",
  aide: "Position finale = solde debut + entrees - sorties.",
  aideEn: "Closing position = opening + inflows - outflows.",
  lister: (params) => api.lister("finc-cash-flow-forecasts", params),
  creer: (data) => api.creer("finc-cash-flow-forecasts", data),
  modifier: (id, data) => api.modifier("finc-cash-flow-forecasts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference prevision", "Forecast reference"),
    col("periode", "Periode", "Period"),
    col("solde_debut", "Solde de debut", "Opening balance"),
    col("entrees_prevues", "Entrees prevues", "Expected inflows"),
    col("sorties_prevues", "Sorties prevues", "Expected outflows"),
    col("position_finale", "Position finale", "Closing position"),
    col("horizon_jours", "Horizon (jours)", "Horizon (days)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference prevision", "Forecast reference", { requisCreation: true }),
    txt("periode", "Periode", "Period"),
    num("solde_debut", "Solde de debut", "Opening balance"),
    num("entrees_prevues", "Entrees prevues", "Expected inflows"),
    num("sorties_prevues", "Sorties prevues", "Expected outflows"),
    num("position_finale", "Position finale", "Closing position"),
    num("horizon_jours", "Horizon (jours)", "Horizon (days)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreFincInvoiceFinancing: ConfigRegistre = {
  permModule: "tresorerie",
  permSousModule: "invoice_financing",
  tcode: "registre-invoice-financing",
  icon: Icons.Coins,
  titre: "Affacturage / escompte de factures",
  titreEn: "Invoice financing",
  description: "Affacturage de factures clients pour accelerer la tresorerie.",
  descriptionEn: "Factoring of client invoices to accelerate treasury.",
  aide: "Le facteur avance un pourcentage de la facture ; marge et risque porteurs.",
  aideEn: "Factor advances a percentage of the invoice; margin and recourse tracked.",
  lister: (params) => api.lister("finc-invoice-financings", params),
  creer: (data) => api.creer("finc-invoice-financings", data),
  modifier: (id, data) => api.modifier("finc-invoice-financings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference dossier", "Facility reference"),
    col("affacteur", "Affacteur", "Factor"),
    col("facture", "Facture cee", "Assigned invoice"),
    col("montant_facture", "Montant facture", "Invoice amount"),
    col("avance_pct", "Avance (%)", "Advance (%)"),
    col("commission", "Commission", "Fee"),
    col("date_echeance", "Echeance facture", "Invoice due date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference dossier", "Facility reference", { requisCreation: true }),
    txt("affacteur", "Affacteur", "Factor"),
    txt("facture", "Facture cee", "Assigned invoice"),
    num("montant_facture", "Montant facture", "Invoice amount"),
    num("avance_pct", "Avance (%)", "Advance (%)"),
    num("commission", "Commission", "Fee"),
    dt("date_echeance", "Echeance facture", "Invoice due date"),
    txt("statut", "Statut", "Status"),
  ],
};

