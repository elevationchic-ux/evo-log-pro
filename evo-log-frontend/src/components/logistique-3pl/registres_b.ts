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

export const registreTplDockAppointment: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "dock_appointment",
  tcode: "registre-dock-appointments",
  icon: Icons.CalendarClock,
  titre: "Rendez-vous quais (dock scheduling)",
  titreEn: "Dock appointments",
  description: "Reservation des creneaux de quai pour chargement/dechargement.",
  descriptionEn: "Dock slot reservation for loading/unloading.",
  aide: "Un creneau par vehicule ; penalite si no-show.",
  aideEn: "One slot per vehicle; no-show penalty.",
  lister: (params) => api.lister("tplb-dock-appointments", params),
  creer: (data) => api.creer("tplb-dock-appointments", data),
  modifier: (id, data) => api.modifier("tplb-dock-appointments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference creneau", "Slot reference"),
    col("site", "Site", "Site"),
    col("numero_quai", "Numero quai", "Dock number"),
    col("date_debut", "Debut", "Start"),
    col("date_fin", "Fin", "End"),
    col("immatriculation", "Immatriculation", "Plate"),
    col("type_mouvement", "Type mouvement", "Movement type"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference creneau", "Slot reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    txt("numero_quai", "Numero quai", "Dock number"),
    dtx("date_debut", "Debut", "Start"),
    dtx("date_fin", "Fin", "End"),
    txt("immatriculation", "Immatriculation", "Plate"),
    txt("type_mouvement", "Type mouvement", "Movement type"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplLoadingPlan: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "loading_plan",
  tcode: "registre-loading-plans",
  icon: Icons.Layers,
  titre: "Plans de chargement camion",
  titreEn: "Truck loading plans",
  description: "Calage et plan de chargement par expedition.",
  descriptionEn: "Stowage and loading plan per shipment.",
  aide: "Verifie charge utile et repartition essieux.",
  aideEn: "Checks payload and axle load.",
  lister: (params) => api.lister("tplb-loading-plans", params),
  creer: (data) => api.creer("tplb-loading-plans", data),
  modifier: (id, data) => api.modifier("tplb-loading-plans", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference plan", "Plan reference"),
    col("site", "Site", "Site"),
    col("numero_camion", "Camion", "Truck"),
    col("nb_colis", "Nb colis", "Parcels"),
    col("poids_total_kg", "Poids total (kg)", "Total weight (kg)"),
    col("volume_m3", "Volume (m3)", "Volume (m3)"),
    col("taux_remplissage_pct", "Taux remplissage (%)", "Fill rate (%)"),
    col("date_plan", "Date plan", "Plan date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference plan", "Plan reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    txt("numero_camion", "Camion", "Truck"),
    num("nb_colis", "Nb colis", "Parcels"),
    num("poids_total_kg", "Poids total (kg)", "Total weight (kg)"),
    num("volume_m3", "Volume (m3)", "Volume (m3)"),
    num("taux_remplissage_pct", "Taux remplissage (%)", "Fill rate (%)"),
    dtx("date_plan", "Date plan", "Plan date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplShipmentManifest: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "shipment_manifest",
  tcode: "registre-shipment-manifests",
  icon: Icons.ScrollText,
  titre: "Manifestes d' expedition",
  titreEn: "Shipment manifests",
  description: "Manifeste regroupant les colis d' une expedition.",
  descriptionEn: "Manifest grouping parcels of a shipment.",
  aide: "Document opposable au transporteur.",
  aideEn: "Document enforceable against carrier.",
  lister: (params) => api.lister("tplb-shipment-manifests", params),
  creer: (data) => api.creer("tplb-shipment-manifests", data),
  modifier: (id, data) => api.modifier("tplb-shipment-manifests", id, data),
  unicite: "numero_manifeste",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_manifeste", "Numero manifeste", "Manifest number"),
    col("client", "Client", "Client"),
    col("site_depart", "Site depart", "Origin site"),
    col("site_arrivee", "Site arrivee", "Destination site"),
    col("nb_colis", "Nb colis", "Parcels"),
    col("poids_total_kg", "Poids total (kg)", "Total weight (kg)"),
    col("date_emission", "Date emission", "Issue date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_manifeste", "Numero manifeste", "Manifest number", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("site_depart", "Site depart", "Origin site"),
    txt("site_arrivee", "Site arrivee", "Destination site"),
    num("nb_colis", "Nb colis", "Parcels"),
    num("poids_total_kg", "Poids total (kg)", "Total weight (kg)"),
    dt("date_emission", "Date emission", "Issue date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplInventoryTransfer: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "inventory_transfer",
  tcode: "registre-inventory-transfers",
  icon: Icons.ArrowRightLeft,
  titre: "Transferts inter-entrepots",
  titreEn: "Inter-warehouse transfers",
  description: "Mouvement de stock entre deux sites du donneur d ordre.",
  descriptionEn: "Stock movement between two client sites.",
  aide: "Ecart d inventaire si reception != expedition.",
  aideEn: "Variance if receipt != shipment.",
  lister: (params) => api.lister("tplb-inventory-transfers", params),
  creer: (data) => api.creer("tplb-inventory-transfers", data),
  modifier: (id, data) => api.modifier("tplb-inventory-transfers", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference transfert", "Transfer reference"),
    col("site_source", "Site source", "Source site"),
    col("site_destinataire", "Site destinataire", "Destination site"),
    col("sku", "SKU", "SKU"),
    col("quantite_expediee", "Quantite expediee", "Shipped qty"),
    col("quantite_recue", "Quantite recue", "Received qty"),
    col("date_transfert", "Date transfert", "Transfer date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference transfert", "Transfer reference", { requisCreation: true }),
    txt("site_source", "Site source", "Source site"),
    txt("site_destinataire", "Site destinataire", "Destination site"),
    txt("sku", "SKU", "SKU"),
    num("quantite_expediee", "Quantite expediee", "Shipped qty"),
    num("quantite_recue", "Quantite recue", "Received qty"),
    dt("date_transfert", "Date transfert", "Transfer date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplColdChainLog: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "cold_chain_log",
  tcode: "registre-cold-chain-logs",
  icon: Icons.ThermometerSnowflake,
  titre: "Journal chaine du froid",
  titreEn: "Cold chain logs",
  description: "Releves de temperature des produits sous temperature dirigee.",
  descriptionEn: "Temperature readings for temperature-controlled goods.",
  aide: "Alerte si sortie de plage contractuelle.",
  aideEn: "Alert when out of contractual range.",
  lister: (params) => api.lister("tplb-cold-chain-logs", params),
  creer: (data) => api.creer("tplb-cold-chain-logs", data),
  modifier: (id, data) => api.modifier("tplb-cold-chain-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference releve", "Reading reference"),
    col("site", "Site", "Site"),
    col("produit", "Produit", "Product"),
    col("sonde", "Sonde", "Probe"),
    col("temperature_c", "Temperature (C)", "Temperature (C)"),
    col("plage_min_c", "Plage min (C)", "Min range (C)"),
    col("plage_max_c", "Plage max (C)", "Max range (C)"),
    col("date_releve", "Date releve", "Reading date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference releve", "Reading reference", { requisCreation: true }),
    txt("site", "Site", "Site"),
    txt("produit", "Produit", "Product"),
    txt("sonde", "Sonde", "Probe"),
    num("temperature_c", "Temperature (C)", "Temperature (C)"),
    num("plage_min_c", "Plage min (C)", "Min range (C)"),
    num("plage_max_c", "Plage max (C)", "Max range (C)"),
    dtx("date_releve", "Date releve", "Reading date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplReturnAuthorization: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "return_authorization",
  tcode: "registre-return-authorizations",
  icon: Icons.PackageCheck,
  titre: "Autorisations de retour (RMA)",
  titreEn: "Return authorizations (RMA)",
  description: "Dossiers de retour client acceptes et traces.",
  descriptionEn: "Accepted and tracked customer return files.",
  aide: "Numero RMA requis avant prise en charge.",
  aideEn: "RMA number required before intake.",
  lister: (params) => api.lister("tplb-return-authorizations", params),
  creer: (data) => api.creer("tplb-return-authorizations", data),
  modifier: (id, data) => api.modifier("tplb-return-authorizations", id, data),
  unicite: "numero_rma",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_rma", "Numero RMA", "RMA number"),
    col("client", "Client", "Client"),
    col("commande_originale", "Commande originale", "Original order"),
    col("motif_retour", "Motif retour", "Return reason"),
    col("nb_unites", "Nb unites", "Units"),
    col("date_demande", "Date demande", "Request date"),
    col("decision", "Decision", "Decision"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_rma", "Numero RMA", "RMA number", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("commande_originale", "Commande originale", "Original order"),
    txt("motif_retour", "Motif retour", "Return reason"),
    num("nb_unites", "Nb unites", "Units"),
    dt("date_demande", "Date demande", "Request date"),
    txt("decision", "Decision", "Decision"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplCarrierRate: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "carrier_rate",
  tcode: "registre-carrier-rates",
  icon: Icons.TableProperties,
  titre: "Grille tarifaire transporteurs",
  titreEn: "Carrier rate cards",
  description: "Barèmes transporteurs par zone, poids et tranche.",
  descriptionEn: "Carrier tariffs by zone, weight and bracket.",
  aide: "Sert au calcul de facturation et au choix du transporteur.",
  aideEn: "Drives billing and carrier choice.",
  lister: (params) => api.lister("tplb-carrier-rates", params),
  creer: (data) => api.creer("tplb-carrier-rates", data),
  modifier: (id, data) => api.modifier("tplb-carrier-rates", id, data),
  unicite: "code_tarif",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tarif", "Code tarif", "Rate code"),
    col("transporteur", "Transporteur", "Carrier"),
    col("zone", "Zone", "Zone"),
    col("poids_kg", "Poids (kg)", "Weight (kg)"),
    col("prix_base_xaf", "Prix base (XAF)", "Base price (XAF)"),
    col("prix_par_kg_xaf", "Prix / kg (XAF)", "Price per kg (XAF)"),
    col("validite_debut", "Debut validite", "Valid from"),
    col("validite_fin", "Fin validite", "Valid until"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_tarif", "Code tarif", "Rate code", { requisCreation: true }),
    txt("transporteur", "Transporteur", "Carrier"),
    txt("zone", "Zone", "Zone"),
    num("poids_kg", "Poids (kg)", "Weight (kg)"),
    num("prix_base_xaf", "Prix base (XAF)", "Base price (XAF)"),
    num("prix_par_kg_xaf", "Prix / kg (XAF)", "Price per kg (XAF)"),
    dt("validite_debut", "Debut validite", "Valid from"),
    dt("validite_fin", "Fin validite", "Valid until"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplOrderNode: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "order_node",
  tcode: "registre-order-nodes",
  icon: Icons.GitCommitHorizontal,
  titre: "Jalons de commande (track & trace)",
  titreEn: "Order milestones (track & trace)",
  description: "Points de controle horodate d une commande (prise en charge a livraison).",
  descriptionEn: "Timestamped checkpoints of an order (pickup to delivery).",
  aide: "Alimente la promesse de service au client.",
  aideEn: "Feeds the client service promise.",
  lister: (params) => api.lister("tplb-order-nodes", params),
  creer: (data) => api.creer("tplb-order-nodes", data),
  modifier: (id, data) => api.modifier("tplb-order-nodes", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference jalon", "Milestone reference"),
    col("numero_commande", "Numero commande", "Order number"),
    col("code_jalon", "Code jalon", "Milestone code"),
    col("libelle_jalon", "Libelle", "Label"),
    col("date_horodatage", "Horodatage", "Timestamp"),
    col("lieu", "Lieu", "Location"),
    col("operateur", "Operateur", "Operator"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference jalon", "Milestone reference", { requisCreation: true }),
    txt("numero_commande", "Numero commande", "Order number"),
    txt("code_jalon", "Code jalon", "Milestone code"),
    txt("libelle_jalon", "Libelle", "Label"),
    dtx("date_horodatage", "Horodatage", "Timestamp"),
    txt("lieu", "Lieu", "Location"),
    txt("operateur", "Operateur", "Operator"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTplDamageClaim: ConfigRegistre = {
  permModule: "log3pl",
  permSousModule: "damage_claim",
  tcode: "registre-damage-claims",
  icon: Icons.FileWarning,
  titre: "Reclamations avaries 3PL",
  titreEn: "3PL damage claims",
  description: "Dossiers d avarie et de litige sur les prestations.",
  descriptionEn: "Damage and dispute files on services.",
  aide: "Reserve financee si avarie > seuil.",
  aideEn: "Financial reserve if damage above threshold.",
  lister: (params) => api.lister("tplb-damage-claims", params),
  creer: (data) => api.creer("tplb-damage-claims", data),
  modifier: (id, data) => api.modifier("tplb-damage-claims", id, data),
  unicite: "numero_dossier",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_dossier", "Numero dossier", "Claim number"),
    col("client", "Client", "Client"),
    col("expedition_associee", "Expedition associee", "Linked shipment"),
    col("type_avarie", "Type avarie", "Damage type"),
    col("montant_reclame_xaf", "Montant reclame (XAF)", "Claimed amount (XAF)"),
    col("date_ouverture", "Date ouverture", "Open date"),
    col("date_resolution", "Date resolution", "Resolution date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_dossier", "Numero dossier", "Claim number", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("expedition_associee", "Expedition associee", "Linked shipment"),
    txt("type_avarie", "Type avarie", "Damage type"),
    num("montant_reclame_xaf", "Montant reclame (XAF)", "Claimed amount (XAF)"),
    dt("date_ouverture", "Date ouverture", "Open date"),
    dt("date_resolution", "Date resolution", "Resolution date"),
    txt("statut", "Statut", "Status"),
  ],
};

