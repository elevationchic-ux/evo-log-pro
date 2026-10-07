/**
 * Configs Registre pour logistique-3pl (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("logistique-3pl");

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

export const registreTplContract: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "contracts",
  tcode: "registre-contract-agreements",
  icon: Icons.FileSignature,
  titre: "Contrats cadres 3PL",
  titreEn: "3PL framework contracts",
  description: "Accords de sous-traitance logistique longue duree.",
  descriptionEn: "Long-term logistics outsourcing agreements.",
  aide: "Engage SLA + penalites journalieres.",
  aideEn: "Binds SLA + daily penalties.",
  lister: (params) => api.lister("tpl-contracts", params),
  creer: (data) => api.creer("tpl-contracts", data),
  modifier: (id, data) => api.modifier("tpl-contracts", id, data),
  unicite: "numero_contrat",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_contrat", "Numero contrat", "Contract number"),
    col("client", "Client", "Client"),
    col("perimetre", "Perimetre", "Scope"),
    col("sites_couverts", "Sites couverts", "Sites covered"),
    col("date_debut", "Date debut", "Start date"),
    col("date_fin", "Date fin", "End date"),
    col("valeur_annuelle_xaf", "Valeur annuelle", "Annual value"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_contrat", "Numero contrat", "Contract number", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("perimetre", "Perimetre", "Scope"),
    txt("sites_couverts", "Sites couverts", "Sites covered"),
    dt("date_debut", "Date debut", "Start date"),
    dt("date_fin", "Date fin", "End date"),
    num("valeur_annuelle_xaf", "Valeur annuelle", "Annual value"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplWarehouse: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "warehouses",
  tcode: "registre-warehouse-3pl",
  icon: Icons.Building,
  titre: "Entrepots sous contrat",
  titreEn: "Contracted warehouses",
  description: "Sites 3PL engages avec client donneur d'ordre.",
  descriptionEn: "Sites committed under client contract.",
  aide: "Cartographie multi-sites / capacites par produit.",
  aideEn: "Multi-site map / capacity by product.",
  lister: (params) => api.lister("tpl-warehouses", params),
  creer: (data) => api.creer("tpl-warehouses", data),
  modifier: (id, data) => api.modifier("tpl-warehouses", id, data),
  unicite: "code_site",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_site", "Code site", "Site code"),
    col("nom", "Nom", "Name"),
    col("localisation", "Localisation", "Location"),
    col("surface_m2", "Surface (m2)", "Area (m2)"),
    col("capacite_palettes", "Capacite palettes", "Pallet capacity"),
    col("zones_froides", "Zones froides", "Cold zones"),
    col("contract_associe", "Contrat associe", "Linked contract"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_site", "Code site", "Site code", { requisCreation: true }),
    txt("nom", "Nom", "Name"),
    txt("localisation", "Localisation", "Location"),
    num("surface_m2", "Surface (m2)", "Area (m2)"),
    num("capacite_palettes", "Capacite palettes", "Pallet capacity"),
    chk("zones_froides", "Zones froides", "Cold zones"),
    txt("contract_associe", "Contrat associe", "Linked contract"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplCrossDock: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "crossdock",
  tcode: "registre-crossdock-plans",
  icon: Icons.ArrowLeftRight,
  titre: "Plans cross-dock",
  titreEn: "Cross-dock plans",
  description: "Flux de transit rapide sans stockage.",
  descriptionEn: "Fast-throughput no-storage flows.",
  aide: "Fenetre creneau <4h obligatoire.",
  aideEn: "Mandatory slot <4h.",
  lister: (params) => api.lister("tpl-crossdocks", params),
  creer: (data) => api.creer("tpl-crossdocks", data),
  modifier: (id, data) => api.modifier("tpl-crossdocks", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference plan", "Plan reference"),
    col("site", "Site", "Site"),
    col("date_operation", "Date operation", "Operation date"),
    col("nb_entrees", "Nb entrees", "Inbound count"),
    col("nb_sorties", "Nb sorties", "Outbound count"),
    col("duree_foresee_min", "Duree prevue (min)", "Planned duration (min)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference plan", "Plan reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    dtx("date_operation", "Date operation", "Operation date"),
    num("nb_entrees", "Nb entrees", "Inbound count"),
    num("nb_sorties", "Nb sorties", "Outbound count"),
    num("duree_foresee_min", "Duree prevue (min)", "Planned duration (min)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplPickingLine: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "pickpack",
  tcode: "registre-pick-pack-lines",
  icon: Icons.ClipboardList,
  titre: "Lignes de preparation",
  titreEn: "Picking / packing lines",
  description: "Ordres de preparation client, picking / packing / shipping.",
  descriptionEn: "Client order preparation, picking / packing / shipping.",
  aide: "Tracabilite operateur + temps unitaire.",
  aideEn: "Operator + unit-time traceability.",
  lister: (params) => api.lister("tpl-picking-lines", params),
  creer: (data) => api.creer("tpl-picking-lines", data),
  modifier: (id, data) => api.modifier("tpl-picking-lines", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference ordre", "Order reference"),
    col("site", "Site", "Site"),
    col("client", "Client", "Client"),
    col("type_preparation", "Type preparation", "Picking type"),
    col("nb_lignes", "Nb lignes", "Lines"),
    col("nb_colis", "Nb colis", "Parcels"),
    col("operateur", "Operateur", "Operator"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference ordre", "Order reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    txt("client", "Client", "Client"),
    txt("type_preparation", "Type preparation", "Picking type"),
    num("nb_lignes", "Nb lignes", "Lines"),
    num("nb_colis", "Nb colis", "Parcels"),
    txt("operateur", "Operateur", "Operator"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplSlaKpi: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "slakpi",
  tcode: "registre-kpi-slas",
  icon: Icons.Target,
  titre: "KPI / SLA contractuels",
  titreEn: "SLA / KPI contractual",
  description: "Taux de service, OTIF, erreurs, penalites.",
  descriptionEn: "Service rate, OTIF, errors, penalties.",
  aide: "Revue mensuelle avec client.",
  aideEn: "Monthly client review.",
  lister: (params) => api.lister("tpl-sla-kpis", params),
  creer: (data) => api.creer("tpl-sla-kpis", data),
  modifier: (id, data) => api.modifier("tpl-sla-kpis", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference mesure", "Measure reference"),
    col("contrat_associe", "Contrat", "Contract"),
    col("periode", "Periode", "Period"),
    col("kpi", "KPI", "KPI"),
    col("valeur_cible", "Valeur cible", "Target"),
    col("valeur_reelle", "Valeur reelle", "Actual"),
    col("penalite_appliquee_xaf", "Penalite (XAF)", "Penalty (XAF)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference mesure", "Measure reference", { requisCreation: true }),
    txt("contrat_associe", "Contrat", "Contract"),
    txt("periode", "Periode", "Period"),
    txt("kpi", "KPI", "KPI"),
    txt("valeur_cible", "Valeur cible", "Target"),
    txt("valeur_reelle", "Valeur reelle", "Actual"),
    num("penalite_appliquee_xaf", "Penalite (XAF)", "Penalty (XAF)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplInvoice: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "billing",
  tcode: "registre-billing-3pl",
  icon: Icons.Receipt,
  titre: "Facturation 3PL",
  titreEn: "3PL billing",
  description: "Facturation mensuelle des prestations logistiques.",
  descriptionEn: "Monthly logistics service billing.",
  aide: "Refacturation selon grille + extras.",
  aideEn: "Grid + extras billing.",
  lister: (params) => api.lister("tpl-invoices", params),
  creer: (data) => api.creer("tpl-invoices", data),
  modifier: (id, data) => api.modifier("tpl-invoices", id, data),
  unicite: "numero_facture",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_facture", "Numero facture", "Invoice number"),
    col("client", "Client", "Client"),
    col("periode", "Periode", "Period"),
    col("montant_ht_xaf", "Montant HT (XAF)", "Net amount"),
    col("tva_xaf", "TVA (XAF)", "VAT"),
    col("total_ttc_xaf", "Total TTC (XAF)", "Gross amount"),
    col("date_emission", "Emission", "Issue date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_facture", "Numero facture", "Invoice number", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("periode", "Periode", "Period"),
    num("montant_ht_xaf", "Montant HT (XAF)", "Net amount"),
    num("tva_xaf", "TVA (XAF)", "VAT"),
    num("total_ttc_xaf", "Total TTC (XAF)", "Gross amount"),
    dt("date_emission", "Emission", "Issue date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplInventoryValuation: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "valuation",
  tcode: "registre-inventory-valuation",
  icon: Icons.Scale,
  titre: "Valorisation stock client",
  titreEn: "Client inventory valuation",
  description: "Inventaires periodiques et valorisation aux conditions contractuelles.",
  descriptionEn: "Periodic stock-take under contractual rules.",
  aide: "Ecart >2% declenche expertise.",
  aideEn: ">2% variance triggers expertise.",
  lister: (params) => api.lister("tpl-inventory-valuations", params),
  creer: (data) => api.creer("tpl-inventory-valuations", data),
  modifier: (id, data) => api.modifier("tpl-inventory-valuations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference inventaire", "Stock-take reference"),
    col("site", "Site", "Site"),
    col("client", "Client", "Client"),
    col("date_inventaire", "Date inventaire", "Stock-take date"),
    col("valeur_theorique_xaf", "Valeur theorique", "Theoretical value"),
    col("valeur_physique_xaf", "Valeur physique", "Physical value"),
    col("ecart_pct", "Ecart (%)", "Variance (%)"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference inventaire", "Stock-take reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    txt("client", "Client", "Client"),
    dt("date_inventaire", "Date inventaire", "Stock-take date"),
    num("valeur_theorique_xaf", "Valeur theorique", "Theoretical value"),
    num("valeur_physique_xaf", "Valeur physique", "Physical value"),
    num("ecart_pct", "Ecart (%)", "Variance (%)"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplSubProvider: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "subcontractors",
  tcode: "registre-sub-3pl-providers",
  icon: Icons.Users,
  titre: "Sous-traitants secondaires",
  titreEn: "Sub-contractors",
  description: "Prestataires appeles par le 3PL principal (carriers, handlers).",
  descriptionEn: "Secondary providers engaged by the lead 3PL.",
  aide: "Audit annuel + contrat cadre.",
  aideEn: "Annual audit + master agreement.",
  lister: (params) => api.lister("tpl-sub-providers", params),
  creer: (data) => api.creer("tpl-sub-providers", data),
  modifier: (id, data) => api.modifier("tpl-sub-providers", id, data),
  unicite: "code_fournisseur",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_fournisseur", "Code fournisseur", "Vendor code"),
    col("raison_sociale", "Raison sociale", "Legal name"),
    col("type_prestation", "Type prestation", "Service type"),
    col("zone_couverte", "Zone couverte", "Coverage"),
    col("date_debut_contrat", "Debut contrat", "Contract start"),
    col("date_audit_precedent", "Dernier audit", "Last audit"),
    col("note_qualite", "Note qualite", "Quality score"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_fournisseur", "Code fournisseur", "Vendor code", { requisCreation: true }),
    txt("raison_sociale", "Raison sociale", "Legal name"),
    txt("type_prestation", "Type prestation", "Service type"),
    txt("zone_couverte", "Zone couverte", "Coverage"),
    dt("date_debut_contrat", "Debut contrat", "Contract start"),
    dt("date_audit_precedent", "Dernier audit", "Last audit"),
    txt("note_qualite", "Note qualite", "Quality score"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplReverseOperation: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "reverse",
  tcode: "registre-reverse-logistics",
  icon: Icons.Recycle,
  titre: "Logistique retour / SAV",
  titreEn: "Reverse logistics",
  description: "Retour produit, reconditionnement, recycling, destruction.",
  descriptionEn: "Product returns, refurbish, recycle, dispose.",
  aide: "Tracabilite reglementaire DEEE.",
  aideEn: "WEEE regulatory traceability.",
  lister: (params) => api.lister("tpl-reverse-operations", params),
  creer: (data) => api.creer("tpl-reverse-operations", data),
  modifier: (id, data) => api.modifier("tpl-reverse-operations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("client", "Client", "Client"),
    col("type_operation", "Type operation", "Type"),
    col("nb_unites", "Nb unites", "Units"),
    col("site_prise_en_charge", "Site", "Site"),
    col("date_prise_en_charge", "Prise en charge", "Intake date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("type_operation", "Type operation", "Type"),
    num("nb_unites", "Nb unites", "Units"),
    txt("site_prise_en_charge", "Site", "Site"),
    dt("date_prise_en_charge", "Prise en charge", "Intake date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplControlTower: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "controltower",
  tcode: "registre-control-tower",
  icon: Icons.RadioTower,
  titre: "Tour de controle multi-flux",
  titreEn: "Multi-flow control tower",
  description: "Pilotage transversal commandes, stock, transport, incidents.",
  descriptionEn: "Cross-cutting order/stock/transport/incident command.",
  aide: "Alertes croisees temps reel.",
  aideEn: "Real-time cross alerts.",
  lister: (params) => api.lister("tpl-control-towers", params),
  creer: (data) => api.creer("tpl-control-towers", data),
  modifier: (id, data) => api.modifier("tpl-control-towers", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference session", "Session reference"),
    col("client", "Client", "Client"),
    col("date_horodatage", "Horodatage", "Timestamp"),
    col("nombre_alertes", "Nb alertes", "Alerts count"),
    col("nombre_incidents", "Nb incidents", "Incidents count"),
    col("taux_service_pct", "Taux service (%)", "Service level (%)"),
    col("operateur_tour", "Operateur tour", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference session", "Session reference", { requisCreation: true }),
    txt("client", "Client", "Client"),
    dtx("date_horodatage", "Horodatage", "Timestamp"),
    num("nombre_alertes", "Nb alertes", "Alerts count"),
    num("nombre_incidents", "Nb incidents", "Incidents count"),
    num("taux_service_pct", "Taux service (%)", "Service level (%)"),
    txt("operateur_tour", "Operateur tour", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};

