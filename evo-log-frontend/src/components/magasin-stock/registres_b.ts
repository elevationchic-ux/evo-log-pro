/**
 * Configs Registre pour magasin-stock (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("magasin-stock");

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

export const registreMagasinbStockCount: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "stock_count",
  tcode: "registre-stock-counts",
  icon: Icons.ClipboardList,
  titre: "Comptages d'inventaire",
  titreEn: "Stock counts",
  description: "Confrontation quantite theorique / quantite physique par emplacement.",
  descriptionEn: "Theoretical vs physical quantity check per location.",
  aide: "L'ecart est la difference physique - theorique.",
  aideEn: "Variance is physical minus theoretical.",
  lister: (params) => api.lister("magasinb-stock-counts", params),
  creer: (data) => api.creer("magasinb-stock-counts", data),
  modifier: (id, data) => api.modifier("magasinb-stock-counts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference comptage", "Count reference"),
    col("article", "Article", "Item"),
    col("emplacement", "Emplacement", "Location"),
    col("quantite_theorique", "Quantite theorique", "Theoretical qty"),
    col("quantite_physique", "Quantite physique", "Physical qty"),
    col("ecart", "Ecart", "Variance"),
    col("date_inventaire", "Date d'inventaire", "Count date"),
    col("agent", "Agent", "Agent"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference comptage", "Count reference", { requisCreation: true }),
    txt("article", "Article", "Item"),
    txt("emplacement", "Emplacement", "Location"),
    num("quantite_theorique", "Quantite theorique", "Theoretical qty"),
    num("quantite_physique", "Quantite physique", "Physical qty"),
    num("ecart", "Ecart", "Variance"),
    dt("date_inventaire", "Date d'inventaire", "Count date"),
    txt("agent", "Agent", "Agent"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreMagasinbGoodsReceipt: ConfigRegistre = {
  permModule: "magasin",
  permSousModule: "goods_receipt",
  tcode: "registre-goods-receipts",
  icon: Icons.PackageCheck,
  titre: "Receptions marchandise",
  titreEn: "Goods receipts",
  description: "Enregistrement des entrees en magasin suite a commande fournisseur.",
  descriptionEn: "Record of warehouse inbound following a purchase order.",
  aide: "La reception peut etre partielle ; controle qualite separe.",
  aideEn: "Receipt may be partial; QC is separate.",
  lister: (params) => api.lister("magasinb-goods-receipts", params),
  creer: (data) => api.creer("magasinb-goods-receipts", data),
  modifier: (id, data) => api.modifier("magasinb-goods-receipts", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference reception", "Receipt reference"),
    col("bon_commande", "Bon de commande", "Purchase order"),
    col("fournisseur", "Fournisseur", "Supplier"),
    col("date_reception", "Date reception", "Receipt date"),
    col("nb_articles", "Nombre d'articles", "Line count"),
    col("quantite_recue", "Quantite recue", "Quantity received"),
    col("controles_fait", "Controles faits", "Checks done"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference reception", "Receipt reference", { requisCreation: true }),
    txt("bon_commande", "Bon de commande", "Purchase order"),
    txt("fournisseur", "Fournisseur", "Supplier"),
    dtx("date_reception", "Date reception", "Receipt date"),
    num("nb_articles", "Nombre d'articles", "Line count"),
    num("quantite_recue", "Quantite recue", "Quantity received"),
    chk("controles_fait", "Controles faits", "Checks done"),
    txt("statut", "Statut", "Status"),
  ],
};

