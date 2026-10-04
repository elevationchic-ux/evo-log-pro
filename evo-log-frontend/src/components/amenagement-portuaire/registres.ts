/**
 * Les neuf registres du département Aménagement portuaire & Domaine public.
 *
 * Ce fichier ne contient AUCUNE donnée métier : uniquement la description de
 * ce que le serveur sait déjà écrire (schemas Pydantic de
 * app/schemas/amenagement_portuaire.py, paramètres de query du router
 * /api/v1/amenagement-portuaire). Les vocabulaires (statuts, types d'ouvrage,
 * origines de financement) et les places portuaires sont demandés à l'API,
 * jamais recopiés ici.
 *
 * Le vocabulaire juridique est celui du circuit camerounais réel :
 *  - schéma directeur / plan directeur visé par l'Autorité portuaire (APN) et
 *    approuvé par arrêté/ministériel (MINMIVT) ;
 *  - programmation : fiche technique, visa de maturité (décret n° 2018/0492),
 *    inscription au PIP/CDMT (MINEPAT), visa du contrôle financier et
 *    notification MINFI ;
 *  - passation : DAO, avis COLIFE ou CIP, attribution, réceptions ; PPP sous la
 *    loi n° 2023/008 ;
 *  - domaine : titres domaniaux, concessions et biens reversibles ;
 *  - ouvrages : inventaire du génie civil, dragage et profondeurs ;
 *  - conformité : EIES (loi n° 96/012), permis et autorisations.
 */
import {
  ScrollText,
  HardHat,
  CalendarRange,
  Gavel,
  Stamp,
  FileSignature,
  Building2,
  Waves,
  FileBadge,
} from 'lucide-react';

import { amenagementAPI } from '@/lib/api-client';

import type {
  ChargementRegistre,
  CircuitExterne,
  ConfigRegistre,
} from './typesRegistre';

/** Un champ d'action est toujours requis à la saisie : ces routes consignent
 *  un acte précis, en envoyer une partie vide n'aurait pas de sens. */
const req = (c: ChargementRegistre, cle: string): string => String(c[cle] ?? '').trim();
const optStr = (c: ChargementRegistre, cle: string): string | undefined => {
  const v = String(c[cle] ?? '').trim();
  return v ? v : undefined;
};
const optNum = (c: ChargementRegistre, cle: string): number | undefined => {
  const v = c[cle];
  if (v === undefined || v === null || v === '') return undefined;
  const n = Number(v);
  return Number.isFinite(n) ? n : undefined;
};

/* ═══════════════════════════ 1. Schémas directeurs ══════════════════════════ */

export const registreSchemas: ConfigRegistre = {
  permSousModule: 'schema_directeur',
  tcode: 'KAMT_SCH',
  icon: ScrollText,
  titre: 'Schémas directeurs & périmètres du domaine',
  titreEn: 'Master plans & domain boundaries',
  description:
    'Registre des documents d\u2019orientation domaniale de Douala, Kribi et Limbé : périmètre, horizon, autorité élaboratrice et acte d\u2019approbation.',
  descriptionEn:
    'Register of domain orientation documents for Douala, Kribi and Limbe: boundary, horizon, drafting authority and approval act.',
  aide:
    'Un schéma directeur n\u2019est pas approuvé par ce logiciel : il est élaboré par l\u2019autorité portuaire, visé puis approuvé par l\u2019État. On en enregistre ici la référence et la date réelles, telles qu\u2019au document.',
  aideEn:
    'This software does not approve a master plan: it is drafted by the port authority, then endorsed by the State. Here you record the actual reference and date from the document.',
  lister: (params) => amenagementAPI.listSchemas(params),
  creer: (data) => amenagementAPI.createSchema(data),
  modifier: (id, data) => amenagementAPI.updateSchema(id, data),
  unicite: 'code',
  colonnes: [
    { name: 'code', label: 'Code', labelEn: 'Code', type: 'code', essence: true },
    { name: 'libelle', label: 'Libellé', labelEn: 'Title', type: 'texte', essence: true },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'place' },
    { name: 'type_schema', label: 'Nature', labelEn: 'Type', type: 'enum', nomenclature: 'type_schema' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'enum', nomenclature: 'statut_schema', essence: true },
    { name: 'horizon_debut', label: 'Début', labelEn: 'From', type: 'nombre' },
    { name: 'horizon_fin', label: 'Fin', labelEn: 'To', type: 'nombre' },
    { name: 'superficie_totale_ha', label: 'Assiette', labelEn: 'Area', type: 'nombre', unite: 'ha' },
    { name: 'reference_approbatrice', label: 'Acte d\u2019approbation', labelEn: 'Approval act', type: 'code' },
    { name: 'date_approbation', label: 'Approuvé le', labelEn: 'Approved on', type: 'date' },
    { name: 'date_echeance_revision', label: 'Révision prévue', labelEn: 'Review due', type: 'date' },
  ],
  champs: [
    { name: 'code', label: 'Code du document', labelEn: 'Document code', type: 'texte', requisCreation: true, lectureSeuleEdition: true, aide: 'Référence interne du schéma, unique au registre.' },
    { name: 'libelle', label: 'Libellé', labelEn: 'Title', type: 'texte', requisCreation: true, large: true },
    { name: 'type_schema', label: 'Nature du document', labelEn: 'Document type', type: 'select', nomenclature: 'type_schema' },
    { name: 'port_id', label: 'Place portuaire', labelEn: 'Port place', type: 'select', depuisPlaces: true, aide: 'Liste servie par le référentiel national des ports.' },
    { name: 'statut', label: 'Statut d\u2019élaboration', labelEn: 'Status', type: 'select', nomenclature: 'statut_schema' },
    { name: 'perimetre', label: 'Périmètre décrit', labelEn: 'Described boundary', type: 'zone', large: true, aide: 'Limites du domaine public concerné, reprises de l\u2019arrêté de délimitation.' },
    { name: 'horizon_debut', label: 'Horizon de début', labelEn: 'Horizon start', type: 'nombre', min: 1900, max: 2200 },
    { name: 'horizon_fin', label: 'Horizon de fin', labelEn: 'Horizon end', type: 'nombre', min: 1900, max: 2200 },
    { name: 'autorite_elaboratrice', label: 'Autorité élaboratrice', labelEn: 'Drafting authority', type: 'texte', aide: 'APN, ministère ou bureau d\u2019études, tel que cité au document.' },
    { name: 'reference_approbatrice', label: 'Référence de l\u2019acte approbatif', labelEn: 'Approval reference', type: 'texte', aide: 'Numéro réel du décret ou de l\u2019arrêté.' },
    { name: 'date_approbation', label: 'Date d\u2019approbation', labelEn: 'Approval date', type: 'date' },
    { name: 'date_depot', label: 'Date de dépôt pour visa', labelEn: 'Filing date', type: 'date' },
    { name: 'date_echeance_revision', label: 'Échéance de révision', labelEn: 'Review deadline', type: 'date' },
    { name: 'superficie_totale_ha', label: 'Superficie totale', labelEn: 'Total area', type: 'nombre', unite: 'ha', min: 0 },
    { name: 'surface_eau_ha', label: 'Surface d\u2019eau', labelEn: 'Water surface', type: 'nombre', min: 0 },
    { name: 'cout_elaboration_xaf', label: 'Coût d\u2019élaboration', labelEn: 'Drafting cost', type: 'montant' },
    { name: 'budget_alloue_travaux_xaf', label: 'Budget de travaux alloué', labelEn: 'Works budget', type: 'montant' },
    { name: 'lignes_directrices', label: 'Lignes directrices', labelEn: 'Guidelines', type: 'liste', large: true },
    { name: 'documents_sources', label: 'Documents sources', labelEn: 'Source documents', type: 'liste', large: true, aide: 'Références des pièces officielles sur lesquelles la saisie appuie.' },
    { name: 'source_reference', label: 'Référence de la source saisie', labelEn: 'Source reference', type: 'texte' },
    { name: 'date_verification', label: 'Date de vérification', labelEn: 'Verification date', type: 'date' },
    { name: 'notes', label: 'Notes', labelEn: 'Notes', type: 'zone', large: true },
  ],
  filtres: [
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_schema' },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'select', depuisPlaces: true },
  ],
  actions: [
    {
      id: 'approbation',
      libelle: 'Attester l\u2019approbation',
      libelleEn: 'Record approval',
      action: 'approve',
      avertissement:
        'Le département ne approuve pas un schéma à la place du MINMIVT : il enregistre le numéro et la date de l\u2019arrêté réellement pris.',
      avertissementEn:
        'The department does not approve a plan on behalf of the MINMIVT: it records the number and date of the act actually taken.',
      champs: [
        { name: 'reference_approbatrice', label: 'N° du décret ou arrêté', labelEn: 'Decree/order number', type: 'texte', requisCreation: true },
        { name: 'date_approbation', label: 'Date d\u2019approbation', labelEn: 'Approval date', type: 'date', requisCreation: true },
      ],
      executer: (id, v) => amenagementAPI.approverSchema(id, {
        reference_approbatrice: req(v, 'reference_approbatrice'),
        date_approbation: req(v, 'date_approbation'),
      }),
      succes: 'Acte d\u2019approbation consigné au registre.',
      succesEn: 'Approval act recorded in the register.',
    },
  ],
  circuits: [
    {
      libelle: 'Transmission dématérialisée au MINMIVT / APN pour visa',
      libelleEn: 'Electronic filing to the MINMIVT / APN',
      motif:
        'Aucun dépôt automatique de ces pièces n\u2019existe au Cameroun : la transmission reste un envoi physique ou ministériel, que le logiciel ne peut simuler.',
      motifEn:
        'No automatic filing exists in Cameroon: transmission remains a physical or ministerial process the software cannot simulate.',
      interroger: (id) => amenagementAPI.requestVisaMinmivt(id),
    },
  ],
};

/* ════════════════════════════ 2. Projets d'aménagement ══════════════════════ */

export const registreProjets: ConfigRegistre = {
  permSousModule: 'projet',
  tcode: 'KAMT_PRJ',
  icon: HardHat,
  titre: 'Projets d\u2019aménagement du domaine portuaire',
  titreEn: 'Port development projects',
  description:
    'Portefeuille des opérations de génie portuaire : nature d\u2019ouvrage, financements, maîtrise d\u2019ouvrage et avancement relevé sur chantier.',
  descriptionEn:
    'Portfolio of port engineering operations: structure type, financing, ownership and site progress as surveyed.',
  aide:
    'L\u2019avancement n\u2019est jamais calculé par le logiciel : il est relevé d\u2019un PV de chantier ou d\u2019un décompte. Un pourcentage absent reste « non enregistré », ce qui est une information en soi.',
  aideEn:
    'Progress is never computed by the software: it comes from a site report or payment certificate. A missing percentage stays “not recorded”, which is itself information.',
  lister: (params) => amenagementAPI.listProjets(params),
  creer: (data) => amenagementAPI.createProjet(data),
  modifier: (id, data) => amenagementAPI.updateProjet(id, data),
  supprimer: (id) => amenagementAPI.deleteProjet(id),
  unicite: 'code_projet',
  colonnes: [
    { name: 'code_projet', label: 'Code', labelEn: 'Code', type: 'code', essence: true },
    { name: 'libelle', label: 'Libellé', labelEn: 'Title', type: 'texte', essence: true },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'place' },
    { name: 'type_ouvrage', label: 'Ouvrage', labelEn: 'Structure', type: 'enum', nomenclature: 'type_projet' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'enum', nomenclature: 'statut_projet', essence: true },
    { name: 'cout_previsionnel_xaf', label: 'Coût prévisionnel', labelEn: 'Estimated cost', type: 'montant' },
    { name: 'cout_reel_xaf', label: 'Coût réel', labelEn: 'Actual cost', type: 'montant' },
    { name: 'avancement_physique_pct', label: 'Avanc. physique', labelEn: 'Physical progress', type: 'nombre', unite: '%' },
    { name: 'avancement_financier_pct', label: 'Avanc. financier', labelEn: 'Financial progress', type: 'nombre', unite: '%' },
    { name: 'date_fin_prevue', label: 'Fin prévue', labelEn: 'Planned end', type: 'date' },
    { name: 'maitre_ouvrage', label: 'Maître d\u2019ouvrage', labelEn: 'Owner', type: 'texte' },
    { name: 'reference_fiche_technique', label: 'Fiche technique', labelEn: 'Technical sheet', type: 'code' },
  ],
  champs: [
    { name: 'code_projet', label: 'Code projet', labelEn: 'Project code', type: 'texte', requisCreation: true, lectureSeuleEdition: true },
    { name: 'libelle', label: 'Libellé', labelEn: 'Title', type: 'texte', requisCreation: true, large: true },
    { name: 'description', label: 'Description', labelEn: 'Description', type: 'zone', large: true },
    { name: 'port_id', label: 'Place portuaire', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'type_ouvrage', label: 'Nature de l\u2019ouvrage', labelEn: 'Structure type', type: 'select', nomenclature: 'type_projet' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_projet' },
    { name: 'priorite', label: 'Priorité', labelEn: 'Priority', type: 'texte', aide: 'Appréciation portée au document de planification, recopiée telle quelle.' },
    { name: 'origines_financement', label: 'Origines de financement', labelEn: 'Funding sources', type: 'liste', nomenclature: 'origine_financement', large: true },
    { name: 'cout_previsionnel_xaf', label: 'Coût prévisionnel', labelEn: 'Estimated cost', type: 'montant' },
    { name: 'cout_reel_xaf', label: 'Coût réel', labelEn: 'Actual cost', type: 'montant' },
    { name: 'financement_public_xaf', label: 'Financement public', labelEn: 'Public funding', type: 'montant' },
    { name: 'financement_prive_xaf', label: 'Financement privé', labelEn: 'Private funding', type: 'montant' },
    { name: 'date_debut_prevue', label: 'Début prévu', labelEn: 'Planned start', type: 'date' },
    { name: 'date_fin_prevue', label: 'Fin prévue', labelEn: 'Planned end', type: 'date' },
    { name: 'date_reelle_demarrage', label: 'Démarrage réel', labelEn: 'Actual start', type: 'date' },
    { name: 'date_reelle_achevement', label: 'Achèvement réel', labelEn: 'Actual completion', type: 'date' },
    { name: 'avancement_physique_pct', label: 'Avancement physique', labelEn: 'Physical progress', type: 'nombre', min: 0, max: 100 },
    { name: 'avancement_financier_pct', label: 'Avancement financier', labelEn: 'Financial progress', type: 'nombre', min: 0, max: 100 },
    { name: 'maitre_ouvrage', label: 'Maître d\u2019ouvrage', labelEn: 'Project owner', type: 'texte' },
    { name: 'maitre_doeuvre', label: 'Maîtrise d\u2019œuvre', labelEn: 'Design supervision', type: 'texte' },
    { name: 'bureau_controle', label: 'Bureau de contrôle', labelEn: 'Control office', type: 'texte' },
    { name: 'entreprise_attributaire', label: 'Entreprise attributaire', labelEn: 'Contractor', type: 'texte' },
    { name: 'reference_fiche_technique', label: 'Référence de la fiche technique', labelEn: 'Technical sheet ref.', type: 'texte', aide: 'Numéro attribué par l\u2019administration, pas une référence interne.' },
    { name: 'date_notification_minfi', label: 'Notification MINFI', labelEn: 'MINFI notification', type: 'date' },
    { name: 'eies_obligatoire', label: 'EIES obligatoire', labelEn: 'EIA required', type: 'booleen' },
    { name: 'superficie_impactee_ha', label: 'Superficie impactée', labelEn: 'Affected area', type: 'nombre', min: 0 },
    { name: 'capacite_additionnelle', label: 'Capacité additionnelle', labelEn: 'Added capacity', type: 'texte', aide: 'Ex. « 2 postes porte-conteneurs », telle qu\u2019au document de projet.' },
    { name: 'justificatif_utilite', label: 'Justificatif d\u2019utilité', labelEn: 'Utility justification', type: 'zone', large: true },
    { name: 'risques', label: 'Risques identifiés', labelEn: 'Identified risks', type: 'liste', large: true },
    { name: 'source_reference', label: 'Source de la saisie', labelEn: 'Entry source', type: 'texte' },
    { name: 'date_verification', label: 'Date de vérification', labelEn: 'Verification date', type: 'date' },
    { name: 'notes', label: 'Notes', labelEn: 'Notes', type: 'zone', large: true },
  ],
  filtres: [
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_projet' },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'type_ouvrage', label: 'Ouvrage', labelEn: 'Structure', type: 'select', nomenclature: 'type_projet' },
  ],
  actions: [
    {
      id: 'avancement',
      libelle: 'Relever l\u2019avancement',
      libelleEn: 'Record progress',
      action: 'modify',
      avertissement:
        'Un pourcentage laissé vide reste non enregistré : le logiciel ne remplit pas le suivi avec un date du jour ni une interpolation.',
      avertissementEn:
        'A blank percentage stays unrecorded: the software does not fill tracking with today\u2019s date or interpolation.',
      champs: [
        { name: 'avancement_physique_pct', label: 'Avancement physique (%)', labelEn: 'Physical progress (%)', type: 'nombre', min: 0, max: 100 },
        { name: 'avancement_financier_pct', label: 'Avancement financier (%)', labelEn: 'Financial progress (%)', type: 'nombre', min: 0, max: 100 },
        { name: 'date_releve', label: 'Date du relevé', labelEn: 'Survey date', type: 'date', aide: 'Date du PV, jamais la date de today\u2019s screen.' },
        { name: 'source_reference', label: 'Pièce source', labelEn: 'Source document', type: 'texte', aide: 'PV de chantier, décompte…' },
      ],
      executer: (id, v) => amenagementAPI.saisirAvancement(id, {
        avancement_physique_pct: optNum(v, 'avancement_physique_pct'),
        avancement_financier_pct: optNum(v, 'avancement_financier_pct'),
        date_releve: optStr(v, 'date_releve'),
        source_reference: optStr(v, 'source_reference'),
      }),
      succes: 'Relevé d\u2019avancement enregistré.',
      succesEn: 'Progress survey recorded.',
    },
  ],
};

/* ════════════════════ 3. Programmation & maturité (PIP/CDMT) ════════════════ */

export const registreProgrammation: ConfigRegistre = {
  permSousModule: 'programmation',
  tcode: 'KAMT_PIP',
  icon: CalendarRange,
  titre: 'Programmation, maturité et engagement des crédits',
  titreEn: 'Programming, maturity and credit commitment',
  description:
    'Circuit réel de la ligne d\u2019investissement : fiche technique, visa de maturité, inscription au PIP/CDMT, visa du contrôle financier, notification MINFI.',
  descriptionEn:
    'Actual investment line pipeline: technical sheet, maturity visa, PIP/CDMT registration, financial control visa, MINFI notification.',
  aide:
    'Chaque étape est un acte pris par une commission ou un ministère. Cet écran en consigne la référence et la date ; il ne délivre aucun visa et n\u2019inscrit aucune ligne de lui-même.',
  aideEn:
    'Each step is an act taken by a commission or ministry. This screen records its reference and date; it issues no visa and registers no line by itself.',
  lister: (params) => amenagementAPI.listProgrammation(params),
  creer: (data) => amenagementAPI.createProgrammation(data),
  modifier: (id, data) => amenagementAPI.updateProgrammation(id, data),
  unicite: 'reference_fiche_technique',
  colonnes: [
    { name: 'reference_fiche_technique', label: 'Fiche technique', labelEn: 'Technical sheet', type: 'code', essence: true },
    { name: 'exercice', label: 'Exercice', labelEn: 'Fiscal year', type: 'nombre', essence: true },
    { name: 'objet', label: 'Objet', labelEn: 'Purpose', type: 'texte', essence: true },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'place' },
    { name: 'statut', label: 'Étape du circuit', labelEn: 'Pipeline stage', type: 'enum', nomenclature: 'statut_document_programmation' },
    { name: 'montant_inscrit_xaf', label: 'Montant inscrit', labelEn: 'Registered amount', type: 'montant' },
    { name: 'montant_paye_xaf', label: 'Montant payé', labelEn: 'Paid amount', type: 'montant' },
    { name: 'numero_visa_maturite', label: 'Visa de maturité', labelEn: 'Maturity visa', type: 'code' },
    { name: 'reference_pip_cdmt', label: 'Ligne PIP/CDMT', labelEn: 'PIP/CDMT line', type: 'code' },
    { name: 'numero_engagement', label: 'N° d\u2019engagement', labelEn: 'Commitment no.', type: 'code' },
  ],
  champs: [
    { name: 'reference_fiche_technique', label: 'Référence de la fiche technique', labelEn: 'Technical sheet ref.', type: 'texte', requisCreation: true, lectureSeuleEdition: true, aide: 'Référence réellement attribuée à la fiche ou au dossier technique.' },
    { name: 'exercice', label: 'Exercice', labelEn: 'Fiscal year', type: 'nombre', requisCreation: true, min: 2000, max: 2100 },
    { name: 'objet', label: 'Objet de la ligne', labelEn: 'Line purpose', type: 'zone', requisCreation: true, large: true },
    { name: 'port_id', label: 'Place portuaire', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'montant_inscrit_xaf', label: 'Montant inscrit', labelEn: 'Registered amount', type: 'montant' },
    { name: 'montant_paye_xaf', label: 'Montant payé', labelEn: 'Paid amount', type: 'montant' },
    { name: 'source_financement', label: 'Source de financement', labelEn: 'Funding source', type: 'select', nomenclature: 'origine_financement' },
    { name: 'chapitre', label: 'Chapitre budgétaire', labelEn: 'Budget chapter', type: 'texte' },
    { name: 'statut', label: 'Étape du circuit', labelEn: 'Pipeline stage', type: 'select', nomenclature: 'statut_document_programmation' },
    { name: 'date_presentation', label: 'Date de présentation', labelEn: 'Presentation date', type: 'date' },
    { name: 'numero_visa_maturite', label: 'N° du visa de maturité', labelEn: 'Maturity visa no.', type: 'texte' },
    { name: 'date_visa_maturite', label: 'Date du visa de maturité', labelEn: 'Maturity visa date', type: 'date' },
    { name: 'autorite_visa_maturite', label: 'Autorité du visa de maturité', labelEn: 'Maturity visa authority', type: 'texte', aide: 'Commission technique ou DGPIP, telle que signataire.' },
    { name: 'reference_pip_cdmt', label: 'Ligne au PIP / CDMT', labelEn: 'PIP/CDMT line', type: 'texte' },
    { name: 'date_visa_controle_financier', label: 'Visa du contrôle financier', labelEn: 'Financial control visa', type: 'date' },
    { name: 'autorite_visa', label: 'Contrôleur financier', labelEn: 'Financial controller', type: 'texte' },
    { name: 'numero_engagement', label: 'N° d\u2019engagement', labelEn: 'Commitment no.', type: 'texte' },
    { name: 'date_notification_minfi', label: 'Notification MINFI', labelEn: 'MINFI notification', type: 'date' },
    { name: 'source_reference', label: 'Source de la saisie', labelEn: 'Entry source', type: 'texte' },
    { name: 'date_verification', label: 'Date de vérification', labelEn: 'Verification date', type: 'date' },
    { name: 'notes', label: 'Notes', labelEn: 'Notes', type: 'zone', large: true },
  ],
  filtres: [
    { name: 'exercice', label: 'Exercice', labelEn: 'Fiscal year', type: 'nombre' },
    { name: 'statut', label: 'Étape', labelEn: 'Stage', type: 'select', nomenclature: 'statut_document_programmation' },
  ],
  actions: [
    {
      id: 'visa-maturite',
      libelle: 'Consigner le visa de maturité',
      libelleEn: 'Record maturity visa',
      action: 'approve',
      avertissement:
        'Le visa de maturité (décret n° 2018/0492) est délivré par la commission technique : ici on en enregistre le numéro et la date, on ne l\u2019appose pas.',
      avertissementEn:
        'The maturity visa (decree no. 2018/0492) is issued by the technical committee: here you record its number and date, you do not grant it.',
      champs: [
        { name: 'numero_visa', label: 'N° du visa', labelEn: 'Visa no.', type: 'texte', requisCreation: true },
        { name: 'date_visa', label: 'Date du visa', labelEn: 'Visa date', type: 'date', requisCreation: true },
        { name: 'autorite_visa', label: 'Autorité émettrice', labelEn: 'Issuing authority', type: 'texte', requisCreation: true },
      ],
      executer: (id, v) => amenagementAPI.viserMaturite(id, {
        numero_visa: req(v, 'numero_visa'),
        date_visa: req(v, 'date_visa'),
        autorite_visa: req(v, 'autorite_visa'),
      }),
      succes: 'Visa de maturité consigné.',
      succesEn: 'Maturity visa recorded.',
    },
    {
      id: 'inscription-pip',
      libelle: 'Consigner l\u2019inscription au PIP/CDMT',
      libelleEn: 'Record PIP/CDMT registration',
      action: 'approve',
      avertissement:
        'La programmation relève du MINEPAT : seule la ligne telle que publiée est enregistrée.',
      avertissementEn:
        'Programming belongs to the MINEPAT: only the published line is recorded.',
      champs: [
        { name: 'reference_pip_cdmt', label: 'Référence de la ligne publiée', labelEn: 'Published line ref.', type: 'texte', requisCreation: true },
        { name: 'exercice', label: 'Exercice d\u2019inscription', labelEn: 'Registration year', type: 'nombre', requisCreation: true, min: 2000, max: 2100 },
      ],
      executer: (id, v) => amenagementAPI.inscrirePip(id, {
        reference_pip_cdmt: req(v, 'reference_pip_cdmt'),
        exercice: Number(req(v, 'exercice')),
      }),
      succes: 'Inscription au PIP/CDMT consignée.',
      succesEn: 'PIP/CDMT registration recorded.',
    },
    {
      id: 'visa-controle-financier',
      libelle: 'Consigner le visa du contrôle financier',
      libelleEn: 'Record financial control visa',
      action: 'approve',
      avertissement:
        'Le visa du contrôle financier engage les crédits : il est apposé par le contrôleur, pas par le département.',
      avertissementEn:
        'The financial control visa commits the credits: it is granted by the controller, not by the department.',
      champs: [
        { name: 'date_visa', label: 'Date du visa', labelEn: 'Visa date', type: 'date', requisCreation: true },
        { name: 'autorite_visa', label: 'Contrôleur financier', labelEn: 'Financial controller', type: 'texte', requisCreation: true },
        { name: 'numero_engagement', label: 'N° d\u2019engagement', labelEn: 'Commitment no.', type: 'texte' },
      ],
      executer: (id, v) => amenagementAPI.viserControleFinancier(id, {
        date_visa: req(v, 'date_visa'),
        autorite_visa: req(v, 'autorite_visa'),
        numero_engagement: optStr(v, 'numero_engagement'),
      }),
      succes: 'Visa du contrôle financier consigné.',
      succesEn: 'Financial control visa recorded.',
    },
  ],
  circuits: [
    {
      libelle: 'Notification électronique au MINFI / MINEPAT',
      libelleEn: 'Electronic notification to MINFI / MINEPAT',
      motif:
        'La notification des crédits est un acte budgétaire de l\u2019État, transmis hors système : le module en consigne la date quand la notification papier est reçue.',
      motifEn:
        'Credit notification is a State budgetary act transmitted outside this system: the module records its date once the paper notification is received.',
      interroger: (id) => amenagementAPI.notificationMinfi(id),
    },
  ],
};

/* ═══════════════════════ 4. Marchés publics & contrats de PPP ═══════════════ */

export const registreMarches: ConfigRegistre = {
  permSousModule: 'marche',
  tcode: 'KAMT_MCH',
  icon: Gavel,
  titre: 'Marchés publics d\u2019aménagement & contrats de PPP',
  titreEn: 'Public works contracts & PPP',
  description:
    'Circuit de la passation : dossier d\u2019appel d\u2019offres, avis COLIFE ou CIP, attribution, ordres de service, réceptions et garanties.',
  descriptionEn:
    'Award pipeline: tender documents, COLIFE or CIP advice, award, service orders, acceptances and warranties.',
  aide:
    'Les marchés de travaux relèvent du code des marchés publics ; les partenariats public-privé de la loi n° 2023/008. Le logiciel tient la trace des pièces et des dates, il ne conduit aucune procédure.',
  aideEn:
    'Works contracts follow the public procurement code; partnerships follow law no. 2023/008. The software keeps the paper trail; it conducts no procedure.',
  lister: (params) => amenagementAPI.listMarches(params),
  creer: (data) => amenagementAPI.createMarche(data),
  modifier: (id, data) => amenagementAPI.updateMarche(id, data),
  unicite: 'reference',
  colonnes: [
    { name: 'reference', label: 'Référence', labelEn: 'Reference', type: 'code', essence: true },
    { name: 'designations', label: 'Objet', labelEn: 'Scope', type: 'texte', essence: true },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'place' },
    { name: 'type_marche', label: 'Type', labelEn: 'Type', type: 'enum', nomenclature: 'type_marche' },
    { name: 'code_marche', label: 'Code de procédure', labelEn: 'Procedure code', type: 'enum', nomenclature: 'code_marche' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'enum', nomenclature: 'statut_marche', essence: true },
    { name: 'attributaire', label: 'Attributaire', labelEn: 'Awardee', type: 'texte' },
    { name: 'montant_attribue_xaf', label: 'Montant attribué', labelEn: 'Awarded amount', type: 'montant' },
    { name: 'date_colife', label: 'Avis COLIFE/CIP', labelEn: 'COLIFE/CIP date', type: 'date' },
    { name: 'date_ouverture_chantier', label: 'Ouverture chantier', labelEn: 'Site opening', type: 'date' },
    { name: 'date_reception_definitive', label: 'Réception définitive', labelEn: 'Final acceptance', type: 'date' },
  ],
  champs: [
    { name: 'reference', label: 'Référence du marché', labelEn: 'Contract reference', type: 'texte', requisCreation: true, lectureSeuleEdition: true },
    { name: 'designations', label: 'Désignation des prestations', labelEn: 'Scope of works', type: 'zone', requisCreation: true, large: true },
    { name: 'type_marche', label: 'Type de marché', labelEn: 'Contract type', type: 'select', nomenclature: 'type_marche' },
    { name: 'code_marche', label: 'Code de la procédure', labelEn: 'Procedure code', type: 'select', nomenclature: 'code_marche' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_marche' },
    { name: 'port_id', label: 'Place portuaire', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'procedure_controle', label: 'Contrôle de la procédure', labelEn: 'Procedure control', type: 'texte', aide: 'ORGAIL, contrôle de légalité… mentionné au dossier.' },
    { name: 'dossier_appel_offre', label: 'Référence du DAO', labelEn: 'Tender reference', type: 'texte' },
    { name: 'date_publication_dao', label: 'Publication du DAO', labelEn: 'Tender publication', type: 'date' },
    { name: 'date_remise_offres', label: 'Remise des offres', labelEn: 'Bid submission', type: 'date' },
    { name: 'date_colife', label: 'Séance COLIFE / CIP', labelEn: 'COLIFE / CIP session', type: 'date' },
    { name: 'avis_colife', label: 'Avis rendu', labelEn: 'Committee advice', type: 'texte', aide: 'Avis recopié du PV ; vide tant que la commission ne s\u2019est pas prononcée.' },
    { name: 'date_attribution', label: 'Date d\u2019attribution', labelEn: 'Award date', type: 'date' },
    { name: 'attributaire', label: 'Attributaire', labelEn: 'Awardee', type: 'texte' },
    { name: 'montant_initial_xaf', label: 'Montant initial', labelEn: 'Initial amount', type: 'montant' },
    { name: 'montant_attribue_xaf', label: 'Montant attribué', labelEn: 'Awarded amount', type: 'montant' },
    { name: 'montant_final_xaf', label: 'Montant définitif', labelEn: 'Final amount', type: 'montant' },
    { name: 'part_pmp_pct', label: 'Part sous-traitance PMP', labelEn: 'Local content share', type: 'nombre', min: 0, max: 100 },
    { name: 'avance_demarrage_xaf', label: 'Avance de démarrage', labelEn: 'Start advance', type: 'montant' },
    { name: 'retenue_garantie_pct', label: 'Retenue de garantie', labelEn: 'Retention', type: 'nombre', min: 0, max: 100 },
    { name: 'caution_banque', label: 'Caution bancaire', labelEn: 'Bank guarantee', type: 'texte' },
    { name: 'delai_execution_mois', label: 'Délai d\u2019exécution', labelEn: 'Execution period', type: 'nombre', min: 0 },
    { name: 'date_notification', label: 'Notification (OS)', labelEn: 'Service order date', type: 'date' },
    { name: 'date_ouverture_chantier', label: 'Ouverture du chantier', labelEn: 'Site opening', type: 'date' },
    { name: 'date_reception_provisoire', label: 'Réception provisoire', labelEn: 'Provisional acceptance', type: 'date' },
    { name: 'date_reception_definitive', label: 'Réception définitive', labelEn: 'Final acceptance', type: 'date' },
    { name: 'garant_result_annees', label: 'Garantie de résultat', labelEn: 'Decennial warranty', type: 'nombre', min: 0 },
    { name: 'nrd_max_jours', label: 'Pénalités maximales', labelEn: 'Max penalty days', type: 'nombre', min: 0 },
    { name: 'source_reference', label: 'Source de la saisie', labelEn: 'Entry source', type: 'texte' },
    { name: 'date_verification', label: 'Date de vérification', labelEn: 'Verification date', type: 'date' },
    { name: 'notes', label: 'Notes', labelEn: 'Notes', type: 'zone', large: true },
  ],
  filtres: [
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_marche' },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'select', depuisPlaces: true },
  ],
  actions: [
    {
      id: 'attribution',
      libelle: 'Tracer l\u2019attribution',
      libelleEn: 'Record award',
      action: 'approve',
      avertissement:
        'L\u2019attribution est prononcée par l\u2019organe compétent après avis COLIFE ou CIP : ici on la retrace, on ne la prononce pas.',
      avertissementEn:
        'The award is decided by the competent body after COLIFE or CIP advice: this records it, it does not decide it.',
      champs: [
        { name: 'attributaire', label: 'Attributaire', labelEn: 'Awardee', type: 'texte', requisCreation: true },
        { name: 'date_attribution', label: 'Date de la décision', labelEn: 'Decision date', type: 'date', requisCreation: true },
        { name: 'montant_attribue_xaf', label: 'Montant attribué', labelEn: 'Awarded amount', type: 'montant' },
        { name: 'reference_deliberation', label: 'Référence du PV', labelEn: 'Minutes reference', type: 'texte', aide: 'PV de la COLIFE ou de la CIP.' },
      ],
      executer: (id, v) => amenagementAPI.attribuerMarche(id, {
        attributaire: req(v, 'attributaire'),
        date_attribution: req(v, 'date_attribution'),
        montant_attribue_xaf: optNum(v, 'montant_attribue_xaf'),
        reference_deliberation: optStr(v, 'reference_deliberation'),
      }),
      succes: 'Attribution tracée au registre des marchés.',
      succesEn: 'Award recorded in the contracts register.',
    },
    {
      id: 'reception',
      libelle: 'Consigner une réception',
      libelleEn: 'Record acceptance',
      action: 'approve',
      avertissement:
        'La réception définitive exige une réception provisoire déjà consignée : le serveur le refuse sinon.',
      avertissementEn:
        'Final acceptance requires a recorded provisional acceptance: the server refuses otherwise.',
      champs: [
        { name: 'date_reception', label: 'Date de la réception', labelEn: 'Acceptance date', type: 'date', requisCreation: true },
        { name: 'provisoire', label: 'Réception', labelEn: 'Acceptance kind', type: 'booleen', requisCreation: true, aide: 'Oui = provisoire, Non = définitive.' },
      ],
      executer: (id, v) => amenagementAPI.receptionnerMarche(id, {
        date_reception: req(v, 'date_reception'),
        provisoire: v.provisoire === 'oui' ? true : v.provisoire === 'non' ? false : true,
      }),
      succes: 'Réception consignée.',
      succesEn: 'Acceptance recorded.',
    },
  ],
  circuits: [
    {
      libelle: 'Soumission du dossier à la COLIFE',
      libelleEn: 'Submission of the file to the COLIFE',
      motif:
        'La COLIFE fonctionne par convocation et séance physiques : aucune interface de dépôt n\u2019existe, le module attend l\u2019avis Consigné après séance.',
      motifEn:
        'The COLIFE works through physical convocations and sessions: no filing interface exists, the module awaits the advice recorded after the session.',
      interroger: (id) => amenagementAPI.soumissionColife(id),
    },
  ],
};
