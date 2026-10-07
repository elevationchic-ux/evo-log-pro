/**
 * Configs Registre pour pipeline-oleoduc (expansion generee).
 *
 * Chaque ConfigRegistre est passe en prop au composant generique
 * <RegistreGenerique /> pour rendre table, filtres, formulaire.
 */
"use client";

import * as Icons from 'lucide-react';
import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';
import { registreAPI } from '@/lib/api-client';

const api = registreAPI("pipeline-oleoduc");

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

export const registrePipe2CustodyTransfer: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "custody_transfer",
  tcode: "registre-custody-transfers",
  icon: Icons.ArrowLeftRight,
  titre: "Transferts de custody",
  titreEn: "Custody transfers",
  description: "Transfert de propriete du produit a une interface du pipeline.",
  descriptionEn: "Product ownership transfer at a pipeline interface.",
  aide: "Les volumes delivers vs recus mesurent l' ecart de custody.",
  aideEn: "Delivered vs received volumes measure the custody variance.",
  lister: (params) => api.lister("pipe2-custody-transfers", params),
  creer: (data) => api.creer("pipe2-custody-transfers", data),
  modifier: (id, data) => api.modifier("pipe2-custody-transfers", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("interface", "Interface", "Interface"),
    col("produit", "Produit", "Product"),
    col("volume_livre", "Volume livre", "Delivered volume"),
    col("volume_recu", "Volume recu", "Received volume"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("interface", "Interface", "Interface"),
    txt("produit", "Produit", "Product"),
    num("volume_livre", "Volume livre", "Delivered volume"),
    num("volume_recu", "Volume recu", "Received volume"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2PressureLog: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "pressure_log",
  tcode: "registre-pressure-logs",
  icon: Icons.Gauge,
  titre: "Releves de pression",
  titreEn: "Pressure logs",
  description: "Releve de pression ligne a une station.",
  descriptionEn: "Line pressure reading at a station.",
  aide: "La pression doit rester entre les seuils mini et maxi.",
  aideEn: "Pressure must stay between min and max thresholds.",
  lister: (params) => api.lister("pipe2-pressure-logs", params),
  creer: (data) => api.creer("pipe2-pressure-logs", data),
  modifier: (id, data) => api.modifier("pipe2-pressure-logs", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("station", "Station", "Station"),
    col("pression_bar", "Pression (bar)", "Pressure (bar)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("station", "Station", "Station"),
    num("pression_bar", "Pression (bar)", "Pressure (bar)"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2PumpStationRead: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "pump_station_read",
  tcode: "registre-pump-station-reads",
  icon: Icons.Activity,
  titre: "Releves de station de pompage",
  titreEn: "Pump station reads",
  description: "Releve de fonctionnement d' une station de pompage.",
  descriptionEn: "Operating reading of a pump station.",
  aide: "Le debit et la vibration qualifient la pompe.",
  aideEn: "Flow and vibration qualify the pump.",
  lister: (params) => api.lister("pipe2-pump-station-reads", params),
  creer: (data) => api.creer("pipe2-pump-station-reads", data),
  modifier: (id, data) => api.modifier("pipe2-pump-station-reads", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("station", "Station", "Station"),
    col("debit", "Debit", "Flow rate"),
    col("vibration", "Vibration", "Vibration"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("station", "Station", "Station"),
    num("debit", "Debit", "Flow rate"),
    num("vibration", "Vibration", "Vibration"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2CorrosionReading: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "corrosion_reading",
  tcode: "registre-corrosion-readings",
  icon: Icons.Ruler,
  titre: "Releves de corrosion",
  titreEn: "Corrosion readings",
  description: "Mesure d' epaisseur / corrosion sur la canalisation.",
  descriptionEn: "Wall-thickness / corrosion measurement on the pipeline.",
  aide: "L' epaisseur sous le seuil minimise declenche la reparation.",
  aideEn: "Thickness under minimum triggers repair.",
  lister: (params) => api.lister("pipe2-corrosion-readings", params),
  creer: (data) => api.creer("pipe2-corrosion-readings", data),
  modifier: (id, data) => api.modifier("pipe2-corrosion-readings", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("troncon", "Troncon", "Segment"),
    col("epaisseur_mm", "Epaisseur (mm)", "Thickness (mm)"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("troncon", "Troncon", "Segment"),
    num("epaisseur_mm", "Epaisseur (mm)", "Thickness (mm)"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2FlowCalibration: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "flow_calibration",
  tcode: "registre-flow-calibrations",
  icon: Icons.Target,
  titre: "Etalonnages de debitmetre",
  titreEn: "Flow calibrations",
  description: "Etalonnage d' un debitmetre de transferation.",
  descriptionEn: "Calibration of a custodian transfer meter.",
  aide: "Le coefficient d' etalonnage corrige le volume facture.",
  aideEn: "The calibration factor corrects the billed volume.",
  lister: (params) => api.lister("pipe2-flow-calibrations", params),
  creer: (data) => api.creer("pipe2-flow-calibrations", data),
  modifier: (id, data) => api.modifier("pipe2-flow-calibrations", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("debitmetre", "Debitmetre", "Flow meter"),
    col("coefficient", "Coefficient", "Factor"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("debitmetre", "Debitmetre", "Flow meter"),
    num("coefficient", "Coefficient", "Factor"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2BatchQualityTest: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "batch_quality_test",
  tcode: "registre-batch-quality-tests",
  icon: Icons.FlaskConical,
  titre: "Essais qualite de lot",
  titreEn: "Batch quality tests",
  description: "Analyse qualite d' un lot de produit circulant.",
  descriptionEn: "Quality analysis of a product batch in transit.",
  aide: "La conformite aux specs libere le lot a la delivery.",
  aideEn: "Conformity to specs releases the batch at delivery.",
  lister: (params) => api.lister("pipe2-batch-quality-tests", params),
  creer: (data) => api.creer("pipe2-batch-quality-tests", data),
  modifier: (id, data) => api.modifier("pipe2-batch-quality-tests", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("lot", "Lot", "Batch"),
    col("produit", "Produit", "Product"),
    col("parametre", "Parametre", "Parameter"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("lot", "Lot", "Batch"),
    txt("produit", "Produit", "Product"),
    txt("parametre", "Parametre", "Parameter"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2InterfaceDetection: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "interface_detection",
  tcode: "registre-interface-detections",
  icon: Icons.Crosshair,
  titre: "Detections d' interface",
  titreEn: "Interface detections",
  description: "Detection de la jointure entre deux produits successifs.",
  descriptionEn: "Detection of the join between two successive products.",
  aide: "La perte d' interface alimente le bilan matiere.",
  aideEn: "Interface loss feeds the mass balance.",
  lister: (params) => api.lister("pipe2-interface-detections", params),
  creer: (data) => api.creer("pipe2-interface-detections", data),
  modifier: (id, data) => api.modifier("pipe2-interface-detections", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("troncon", "Troncon", "Segment"),
    col("volume_interface", "Volume interface", "Interface volume"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("troncon", "Troncon", "Segment"),
    num("volume_interface", "Volume interface", "Interface volume"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2IntegrityAssessment: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "integrity_assessment",
  tcode: "registre-integrity-assessments",
  icon: Icons.ShieldCheck,
  titre: "Evaluations d' integrite",
  titreEn: "Integrity assessments",
  description: "Evaluation globale de l' integrite mecanique d' un troncon.",
  descriptionEn: "Overall mechanical integrity assessment of a segment.",
  aide: "Le niveau de risque conditionne la contrainte de pression.",
  aideEn: "The risk level conditions the pressure constraint.",
  lister: (params) => api.lister("pipe2-integrity-assessments", params),
  creer: (data) => api.creer("pipe2-integrity-assessments", data),
  modifier: (id, data) => api.modifier("pipe2-integrity-assessments", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("troncon", "Troncon", "Segment"),
    col("niveau_risque", "Niveau de risque", "Risk level"),
    col("pression_max", "Pression max", "Max pressure"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("troncon", "Troncon", "Segment"),
    txt("niveau_risque", "Niveau de risque", "Risk level"),
    num("pression_max", "Pression max", "Max pressure"),
    dt("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};


export const registrePipe2SpillResponseAction: ConfigRegistre = {
  permModule: "pipeline",
  permSousModule: "spill_response_action",
  tcode: "registre-spill-response-actions",
  icon: Icons.Droplets,
  titre: "Actions de reponse a deversement",
  titreEn: "Spill response actions",
  description: "Action declenchee suite a un deversement detecte.",
  descriptionEn: "Action triggered after a detected spill.",
  aide: "Le volume recupere et la cloture attestent la maitrise.",
  aideEn: "Recovered volume and closure evidence containment.",
  lister: (params) => api.lister("pipe2-spill-response-actions", params),
  creer: (data) => api.creer("pipe2-spill-response-actions", data),
  modifier: (id, data) => api.modifier("pipe2-spill-response-actions", id, data),
  unicite: "reference",
  fetchNomenclatures: () => api.getNomenclatures(),
  colonnes: [
    col("reference", "Reference", "Reference"),
    col("lieu", "Lieu", "Location"),
    col("volume_rejete", "Volume rejete", "Released volume"),
    col("volume_recupere", "Volume recupere", "Recovered volume"),
    col("date", "Date", "Date"),
    col("statut", "Statut", "Status"),
  ],
  champs: [
    txt("reference", "Reference", "Reference", { requisCreation: true }),
    txt("lieu", "Lieu", "Location"),
    num("volume_rejete", "Volume rejete", "Released volume"),
    num("volume_recupere", "Volume recupere", "Recovered volume"),
    dtx("date", "Date", "Date"),
    txt("statut", "Statut", "Status"),
  ],
};

