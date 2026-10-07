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

export const registreCommCompetitorNote: ConfigRegistre = {
  permModule: "b2b",
  permSousModule: "competitor_note",
  tcode: "registre-competitor-notes",
  icon: Icons.Radar,
  titre: "Notes de veille concurrence",
  titreEn: "Competitor notes",
  description: "Observation de veille concurrentielle saisie par le commercial.",
  descriptionEn: "Competitive-intelligence observation captured by the salesperson.",
  aide: "Le concurrent et le fait observe alimentent la strategie.",
  aideEn: "The competitor and observed fact feed the strategy.",
  lister: (params) => api.lister("comm-competitor-notes", params),
  creer: (data) => api.creer("comm-competitor-notes", data),
  modifier: (id, data) => api.modifier("comm-competitor-notes", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("concurrent", "Concurrent", "Competitor"),
    col("fait_observe", "Fait observe", "Observed fact"),
    col("marche", "Marche", "Market"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("concurrent", "Concurrent", "Competitor"),
    txt("fait_observe", "Fait observe", "Observed fact"),
    txt("marche", "Marche", "Market"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

