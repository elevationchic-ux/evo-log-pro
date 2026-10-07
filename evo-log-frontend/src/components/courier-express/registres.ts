/**
 * Configs Registre pour courier-express (expansion wave 5 generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("courier-express");

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


export const registreParcel: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "parcels",
  tcode: "registre-parcels",
  icon: Icons.Package,
  titre: "Colis",
  titreEn: "Parcels",
  description: "Unites de transport suivies du leve a la livraison.",
  descriptionEn: "Units tracked from pickup to delivery.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("parcels", params),
  creer: (data) => api.creer("parcels", data),
  modifier: (id, data) => api.modifier("parcels", id, data),
  unicite: "numero_colis",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_colis", "Numero Colis", "Parcel number"),
    col("type_colis", "Type Colis", "Type Colis"),
    col("format", "Format", "Format"),
    col("poids_kg", "Poids (kg)", "Poids Kg"),
    col("dimensions_cm", "Dimensions Cm", "Dimensions Cm"),
    col("valeur_declaree_xaf", "Valeur Declaree Xaf", "Valeur Declaree Xaf"),
    col("expediteur", "Expediteur", "Expediteur"),
    col("destinataire", "Destinataire", "Destinataire"),
    col("date_prise_en_charge", "Date Prise En Charge", "Date Prise En Charge"),
    col("date_livraison", "Date Livraison", "Date Livraison"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_colis", "Numero Colis", "Parcel number", { requisCreation: true }),
    txt("type_colis", "Type Colis", "Type Colis"),
    txt("format", "Format", "Format"),
    num("poids_kg", "Poids (kg)", "Poids Kg"),
    txt("dimensions_cm", "Dimensions Cm", "Dimensions Cm"),
    num("valeur_declaree_xaf", "Valeur Declaree Xaf", "Valeur Declaree Xaf"),
    txt("expediteur", "Expediteur", "Expediteur"),
    txt("destinataire", "Destinataire", "Destinataire"),
    dt("date_prise_en_charge", "Date Prise En Charge", "Date Prise En Charge"),
    dt("date_livraison", "Date Livraison", "Date Livraison"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreWaybill: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "waybills",
  tcode: "registre-waybills",
  icon: Icons.FileText,
  titre: "Lettres de voiture express (LSE)",
  titreEn: "Express waybills",
  description: "Titre de transport multi-colis par client.",
  descriptionEn: "Multi-parcel transport title per client.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("waybills", params),
  creer: (data) => api.creer("waybills", data),
  modifier: (id, data) => api.modifier("waybills", id, data),
  unicite: "numero_lse",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("numero_lse", "Numero Lse", "Waybill number"),
    col("type_service", "Type Service", "Type Service"),
    col("client", "Client", "Client"),
    col("nb_colis", "Nb Colis", "Nb Colis"),
    col("poids_total_kg", "Poids Total Kg", "Poids Total Kg"),
    col("montant_facture_xaf", "Montant Facture Xaf", "Montant Facture Xaf"),
    col("date_emission", "Date Emission", "Date Emission"),
    col("date_livraison_prevue", "Date Livraison Prevue", "Date Livraison Prevue"),
    col("date_livraison_reelle", "Date Livraison Reelle", "Date Livraison Reelle"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("numero_lse", "Numero Lse", "Waybill number", { requisCreation: true }),
    txt("type_service", "Type Service", "Type Service"),
    txt("client", "Client", "Client"),
    num("nb_colis", "Nb Colis", "Nb Colis"),
    num("poids_total_kg", "Poids Total Kg", "Poids Total Kg"),
    num("montant_facture_xaf", "Montant Facture Xaf", "Montant Facture Xaf"),
    dt("date_emission", "Date Emission", "Date Emission"),
    dt("date_livraison_prevue", "Date Livraison Prevue", "Date Livraison Prevue"),
    dt("date_livraison_reelle", "Date Livraison Reelle", "Date Livraison Reelle"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreHub: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "hubs",
  tcode: "registre-hubs",
  icon: Icons.Building2,
  titre: "Hubs / centres de tri",
  titreEn: "Sorting hubs",
  description: "Plates-formes de tri amont/aval.",
  descriptionEn: "Upstream/downstream sort platforms.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("hubs", params),
  creer: (data) => api.creer("hubs", data),
  modifier: (id, data) => api.modifier("hubs", id, data),
  unicite: "code_hub",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_hub", "Code Hub", "Hub code"),
    col("nom", "Nom", "Nom"),
    col("ville", "Ville", "Ville"),
    col("pays", "Pays", "Pays"),
    col("capacite", "Capacite", "Capacite"),
    col("nb_tri_jour", "Nb Tri Jour", "Nb Tri Jour"),
    col("surface_m2", "Surface M2", "Surface M2"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_hub", "Code Hub", "Hub code", { requisCreation: true }),
    txt("nom", "Nom", "Nom"),
    txt("ville", "Ville", "Ville"),
    txt("pays", "Pays", "Pays"),
    txt("capacite", "Capacite", "Capacite"),
    num("nb_tri_jour", "Nb Tri Jour", "Nb Tri Jour"),
    num("surface_m2", "Surface M2", "Surface M2"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreDeliveryZone: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "delivery_zones",
  tcode: "registre-delivery-zones",
  icon: Icons.Map,
  titre: "Zones de livraison",
  titreEn: "Delivery zones",
  description: "Decoupage geographique avec tarification.",
  descriptionEn: "Geographic zoning with pricing.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("delivery-zones", params),
  creer: (data) => api.creer("delivery-zones", data),
  modifier: (id, data) => api.modifier("delivery-zones", id, data),
  unicite: "code_zone",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_zone", "Code Zone", "Zone code"),
    col("nom", "Nom", "Nom"),
    col("type_zone", "Type Zone", "Type Zone"),
    col("ville", "Ville", "Ville"),
    col("nb_habitants", "Nb Habitants", "Nb Habitants"),
    col("nb_colis_jour", "Nb Colis Jour", "Nb Colis Jour"),
    col("hub_rattachement", "Hub Rattachement", "Hub Rattachement"),
    col("surcost_xaf", "Surcost Xaf", "Surcost Xaf"),
  ],
  champs: [
    txt("code_zone", "Code Zone", "Zone code", { requisCreation: true }),
    txt("nom", "Nom", "Nom"),
    txt("type_zone", "Type Zone", "Type Zone"),
    txt("ville", "Ville", "Ville"),
    num("nb_habitants", "Nb Habitants", "Nb Habitants"),
    num("nb_colis_jour", "Nb Colis Jour", "Nb Colis Jour"),
    txt("hub_rattachement", "Hub Rattachement", "Hub Rattachement"),
    num("surcost_xaf", "Surcost Xaf", "Surcost Xaf"),
  ],
};


export const registreRoute: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "routes",
  tcode: "registre-routes",
  icon: Icons.Route,
  titre: "Tournees de livraison",
  titreEn: "Delivery routes",
  description: "Tourneeh tournee du vehicule sur une journee.",
  descriptionEn: "Daily vehicle route plan.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("routes", params),
  creer: (data) => api.creer("routes", data),
  modifier: (id, data) => api.modifier("routes", id, data),
  unicite: "code_tournee",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tournee", "Code Tournee", "Route code"),
    col("type_route", "Type Route", "Type Route"),
    col("zone_associee", "Zone Associee", "Zone Associee"),
    col("chauffeur", "Chauffeur", "Chauffeur"),
    col("vehicule", "Vehicule", "Vehicule"),
    col("date_tournee", "Date Tournee", "Date Tournee"),
    col("nb_arrets", "Nb Arrets", "Nb Arrets"),
    col("distance_km", "Distance (km)", "Distance Km"),
    col("duree_h", "Duree H", "Duree H"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_tournee", "Code Tournee", "Route code", { requisCreation: true }),
    txt("type_route", "Type Route", "Type Route"),
    txt("zone_associee", "Zone Associee", "Zone Associee"),
    txt("chauffeur", "Chauffeur", "Chauffeur"),
    txt("vehicule", "Vehicule", "Vehicule"),
    dt("date_tournee", "Date Tournee", "Date Tournee"),
    num("nb_arrets", "Nb Arrets", "Nb Arrets"),
    num("distance_km", "Distance (km)", "Distance Km"),
    num("duree_h", "Duree H", "Duree H"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreCourier: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "couriers",
  tcode: "registre-couriers",
  icon: Icons.User,
  titre: "Coursiers / livreurs",
  titreEn: "Couriers",
  description: "Personnel de collecte et livraison.",
  descriptionEn: "Pickup & delivery personnel.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("couriers", params),
  creer: (data) => api.creer("couriers", data),
  modifier: (id, data) => api.modifier("couriers", id, data),
  unicite: "code_coursier",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_coursier", "Code Coursier", "Courier code"),
    col("nom", "Nom", "Nom"),
    col("telephone", "Telephone", "Telephone"),
    col("email", "Email", "Email"),
    col("type_contrat", "Type Contrat", "Type Contrat"),
    col("permis_conduire", "Permis Conduire", "Permis Conduire"),
    col("date_embauche", "Date Embauche", "Date Embauche"),
    col("nb_livraisons_jour", "Nb Livraisons Jour", "Nb Livraisons Jour"),
    col("taux_ponctualite_pct", "Taux Ponctualite Pct", "Taux Ponctualite Pct"),
    col("disponibilite", "Disponibilite", "Disponibilite"),
  ],
  champs: [
    txt("code_coursier", "Code Coursier", "Courier code", { requisCreation: true }),
    txt("nom", "Nom", "Nom"),
    txt("telephone", "Telephone", "Telephone"),
    txt("email", "Email", "Email"),
    txt("type_contrat", "Type Contrat", "Type Contrat"),
    txt("permis_conduire", "Permis Conduire", "Permis Conduire"),
    dt("date_embauche", "Date Embauche", "Date Embauche"),
    num("nb_livraisons_jour", "Nb Livraisons Jour", "Nb Livraisons Jour"),
    num("taux_ponctualite_pct", "Taux Ponctualite Pct", "Taux Ponctualite Pct"),
    txt("disponibilite", "Disponibilite", "Disponibilite"),
  ],
};


export const registrePod: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "pods",
  tcode: "registre-pods",
  icon: Icons.CheckCircle,
  titre: "Preuve de livraison (POD)",
  titreEn: "Proof of delivery",
  description: "Scan signature + photo du destinataire.",
  descriptionEn: "Signature scan + recipient photo.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("pods", params),
  creer: (data) => api.creer("pods", data),
  modifier: (id, data) => api.modifier("pods", id, data),
  unicite: "reference_pod",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference_pod", "Reference Pod", "POD reference"),
    col("numero_colis", "Numero Colis", "Parcel number"),
    col("date_livraison", "Date Livraison", "Date Livraison"),
    col("destination_finale", "Destination Finale", "Destination Finale"),
    col("agent_livreur", "Agent Livreur", "Agent Livreur"),
    col("resultat", "Resultat", "Resultat"),
    col("signature_recu", "Signature Recu", "Signature Recu"),
    col("photo_url", "Photo Url", "Photo Url"),
    col("geo_lat", "Geo Lat", "Geo Lat"),
    col("geo_lon", "Geo Lon", "Geo Lon"),
  ],
  champs: [
    txt("reference_pod", "Reference Pod", "POD reference", { requisCreation: true }),
    txt("numero_colis", "Numero Colis", "Parcel number"),
    dtx("date_livraison", "Date Livraison", "Date Livraison"),
    txt("destination_finale", "Destination Finale", "Destination Finale"),
    txt("agent_livreur", "Agent Livreur", "Agent Livreur"),
    txt("resultat", "Resultat", "Resultat"),
    chk("signature_recu", "Signature Recu", "Signature Recu"),
    txt("photo_url", "Photo Url", "Photo Url"),
    txt("geo_lat", "Geo Lat", "Geo Lat"),
    txt("geo_lon", "Geo Lon", "Geo Lon"),
  ],
};


export const registreSla: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "slas",
  tcode: "registre-slas",
  icon: Icons.Timer,
  titre: "Accords de niveau service (SLA)",
  titreEn: "Service level agreements",
  description: "Engagements délai + pénalités par client.",
  descriptionEn: "Delay commitment + penalty per client.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("slas", params),
  creer: (data) => api.creer("slas", data),
  modifier: (id, data) => api.modifier("slas", id, data),
  unicite: "code_sla",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_sla", "Code Sla", "SLA code"),
    col("client", "Client", "Client"),
    col("categorie", "Categorie", "Categorie"),
    col("engagement_pct", "Engagement Pct", "Engagement Pct"),
    col("delai_h", "Delai H", "Delai H"),
    col("penalite_xaf", "Penalite Xaf", "Penalite Xaf"),
    col("mesure_pct", "Mesure Pct", "Mesure Pct"),
    col("date_debut", "Date debut", "Date Debut"),
    col("date_fin", "Date fin", "Date Fin"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_sla", "Code Sla", "SLA code", { requisCreation: true }),
    txt("client", "Client", "Client"),
    txt("categorie", "Categorie", "Categorie"),
    num("engagement_pct", "Engagement Pct", "Engagement Pct"),
    num("delai_h", "Delai H", "Delai H"),
    num("penalite_xaf", "Penalite Xaf", "Penalite Xaf"),
    num("mesure_pct", "Mesure Pct", "Mesure Pct"),
    dt("date_debut", "Date debut", "Date Debut"),
    dt("date_fin", "Date fin", "Date Fin"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreLocker: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "lockers",
  tcode: "registre-lockers",
  icon: Icons.Lock,
  titre: "Casiers automatiques",
  titreEn: "Smart lockers",
  description: "Points de retrait libres-service.",
  descriptionEn: "Self-service pickup points.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("lockers", params),
  creer: (data) => api.creer("lockers", data),
  modifier: (id, data) => api.modifier("lockers", id, data),
  unicite: "code_locker",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_locker", "Code Locker", "Locker code"),
    col("adresse", "Adresse", "Adresse"),
    col("ville", "Ville", "Ville"),
    col("nb_cases", "Nb Cases", "Nb Cases"),
    col("nb_cases_libres", "Nb Cases Libres", "Nb Cases Libres"),
    col("type_acces", "Type Acces", "Type Acces"),
    col("horaires_ouverture", "Horaires Ouverture", "Horaires Ouverture"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_locker", "Code Locker", "Locker code", { requisCreation: true }),
    txt("adresse", "Adresse", "Adresse"),
    txt("ville", "Ville", "Ville"),
    num("nb_cases", "Nb Cases", "Nb Cases"),
    num("nb_cases_libres", "Nb Cases Libres", "Nb Cases Libres"),
    txt("type_acces", "Type Acces", "Type Acces"),
    txt("horaires_ouverture", "Horaires Ouverture", "Horaires Ouverture"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreVehiculeEx: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "vehicules",
  tcode: "registre-vehicules",
  icon: Icons.Truck,
  titre: "Vehicules de livraison",
  titreEn: "Delivery vehicles",
  description: "Moto / utilitaire / poids lourd.",
  descriptionEn: "Motorcycle / van / truck.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("vehicules", params),
  creer: (data) => api.creer("vehicules", data),
  modifier: (id, data) => api.modifier("vehicules", id, data),
  unicite: "plaque",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("plaque", "Plaque", "Plate"),
    col("type_vehicule", "Type Vehicule", "Type Vehicule"),
    col("marque", "Marque", "Marque"),
    col("modele", "Modele", "Modele"),
    col("capacite_m3", "Capacite M3", "Capacite M3"),
    col("date_mise_circulation", "Date Mise Circulation", "Date Mise Circulation"),
    col("kilometrage_actuel", "Kilometrage Actuel", "Kilometrage Actuel"),
    col("prochaine_revision_km", "Prochaine Revision Km", "Prochaine Revision Km"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("plaque", "Plaque", "Plate", { requisCreation: true }),
    txt("type_vehicule", "Type Vehicule", "Type Vehicule"),
    txt("marque", "Marque", "Marque"),
    txt("modele", "Modele", "Modele"),
    num("capacite_m3", "Capacite M3", "Capacite M3"),
    dt("date_mise_circulation", "Date Mise Circulation", "Date Mise Circulation"),
    num("kilometrage_actuel", "Kilometrage Actuel", "Kilometrage Actuel"),
    num("prochaine_revision_km", "Prochaine Revision Km", "Prochaine Revision Km"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreTarifEx: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "tarifs",
  tcode: "registre-tarifs",
  icon: Icons.Calculator,
  titre: "Tarification express",
  titreEn: "Express tariffs",
  description: "Poids / volume / zone / urgence.",
  descriptionEn: "Weight / volume / zone / urgency.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("tarifs", params),
  creer: (data) => api.creer("tarifs", data),
  modifier: (id, data) => api.modifier("tarifs", id, data),
  unicite: "code_tarif",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("code_tarif", "Code Tarif", "Tariff code"),
    col("zone_tarifaire", "Zone Tarifaire", "Zone Tarifaire"),
    col("tranche_poids_kg", "Tranche Poids Kg", "Tranche Poids Kg"),
    col("prix_base_xaf", "Prix Base Xaf", "Prix Base Xaf"),
    col("prix_par_kg_supp_xaf", "Prix Par Kg Supp Xaf", "Prix Par Kg Supp Xaf"),
    col("options_payantes", "Options Payantes", "Options Payantes"),
    col("date_debut_validite", "Date Debut Validite", "Date Debut Validite"),
    col("date_fin_validite", "Date Fin Validite", "Date Fin Validite"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("code_tarif", "Code Tarif", "Tariff code", { requisCreation: true }),
    txt("zone_tarifaire", "Zone Tarifaire", "Zone Tarifaire"),
    txt("tranche_poids_kg", "Tranche Poids Kg", "Tranche Poids Kg"),
    num("prix_base_xaf", "Prix Base Xaf", "Prix Base Xaf"),
    num("prix_par_kg_supp_xaf", "Prix Par Kg Supp Xaf", "Prix Par Kg Supp Xaf"),
    area("options_payantes", "Options Payantes", "Options Payantes"),
    dt("date_debut_validite", "Date Debut Validite", "Date Debut Validite"),
    dt("date_fin_validite", "Date Fin Validite", "Date Fin Validite"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registreExceptionEx: ConfigRegistre = {
  permModule: "courier",
  permSousModule: "exceptions",
  tcode: "registre-exceptions",
  icon: Icons.AlertOctagon,
  titre: "Exceptions & litiges colis",
  titreEn: "Parcel exceptions",
  description: "Colis perdu / endommage / retard.",
  descriptionEn: "Lost / damaged / delayed parcel.",
  aide: "Registre genere (expansion wave 5).",
  aideEn: "Generated register (wave 5 expansion).",
  lister: (params) => api.lister("exceptions", params),
  creer: (data) => api.creer("exceptions", data),
  modifier: (id, data) => api.modifier("exceptions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("numero_colis", "Numero Colis", "Parcel number"),
    col("type_exception", "Type Exception", "Type Exception"),
    col("date_signalement", "Date Signalement", "Date Signalement"),
    col("description", "Description", "Description"),
    col("montant_litige_xaf", "Montant Litige Xaf", "Montant Litige Xaf"),
    col("agent", "Agent", "Agent"),
    col("date_resolution", "Date Resolution", "Date Resolution"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("numero_colis", "Numero Colis", "Parcel number"),
    txt("type_exception", "Type Exception", "Type Exception"),
    dtx("date_signalement", "Date Signalement", "Date Signalement"),
    area("description", "Description", "Description"),
    num("montant_litige_xaf", "Montant Litige Xaf", "Montant Litige Xaf"),
    txt("agent", "Agent", "Agent"),
    dtx("date_resolution", "Date Resolution", "Date Resolution"),
    txt("statut", "Statut", "Status"),
  ],
};

