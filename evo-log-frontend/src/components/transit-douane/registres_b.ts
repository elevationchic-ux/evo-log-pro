/**
 * Configs Registre pour transit-douane (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("transit-douane");

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

export const registreTransitbIncoterm: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "incoterm_term",
  tcode: "registre-incoterm-terms",
  icon: Icons.Scale,
  titre: "Incoterms applicables",
  titreEn: "Incoterm terms",
  description: "Referentiel des incoterms et de leur version.",
  descriptionEn: "Reference of incoterms and their version.",
  aide: "Le transfert de risque et le lieu font la valeur de l'incoterm.",
  aideEn: "Risk transfer point and place define the incoterm.",
  lister: (params) => api.lister("transitb-incoterms", params),
  creer: (data) => api.creer("transitb-incoterms", data),
  modifier: (id, data) => api.modifier("transitb-incoterms", id, data),
  unicite: "code",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code", "Code incoterm", "Incoterm code"),
    col("libelle", "Libelle", "Label"),
    col("categorie", "Categorie", "Category"),
    col("transfert_risque_lieu", "Lieu transfert risque", "Risk transfer place"),
    col("transport_principal", "Transport principal", "Main carriage"),
    col("version", "Version", "Version"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code", "Code incoterm", "Incoterm code", { requisCreation: true }),
    txt("libelle", "Libelle", "Label"),
    txt("categorie", "Categorie", "Category"),
    txt("transfert_risque_lieu", "Lieu transfert risque", "Risk transfer place"),
    txt("transport_principal", "Transport principal", "Main carriage"),
    txt("version", "Version", "Version"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTransitbInspectionRecord: ConfigRegistre = {
  permModule: "transit",
  permSousModule: "inspection_record",
  tcode: "registre-customs-inspection-records",
  icon: Icons.SearchCheck,
  titre: "Proces-verbaux de visite douaniere",
  titreEn: "Customs inspection records",
  description: "Consigne des visites (documentaire, physique, radiographie) et resultats.",
  descriptionEn: "Log of customs examinations (document, physical, x-ray) and outcomes.",
  aide: "Chaque visite a un agent responsable et un resultat trace.",
  aideEn: "Each inspection has a responsible officer and a recorded outcome.",
  lister: (params) => api.lister("transitb-customs-inspections", params),
  creer: (data) => api.creer("transitb-customs-inspections", data),
  modifier: (id, data) => api.modifier("transitb-customs-inspections", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference visite", "Inspection reference"),
    col("declaration", "Declaration", "Declaration"),
    col("type_visite", "Type de visite", "Inspection type"),
    col("agent", "Agent", "Officer"),
    col("bureau", "Bureau", "Office"),
    col("date_inspection", "Date inspection", "Inspection date"),
    col("observation", "Observation", "Observation"),
    col("conformite", "Conforme", "Compliant"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference visite", "Inspection reference", { requisCreation: true }),
    txt("declaration", "Declaration", "Declaration"),
    txt("type_visite", "Type de visite", "Inspection type"),
    txt("agent", "Agent", "Officer"),
    txt("bureau", "Bureau", "Office"),
    dtx("date_inspection", "Date inspection", "Inspection date"),
    txt("observation", "Observation", "Observation"),
    chk("conformite", "Conforme", "Compliant"),
    txt("statut", "Statut", "Status"),
  ],
};

