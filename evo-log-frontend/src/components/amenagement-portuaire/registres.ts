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
        'Le département n’approuve pas un schéma à la place du MINMIVT : il enregistre le numéro et la date de l’arrêté réellement pris.',
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
  // Aucun bouton de suppression sèche : la route DELETE du serveur exige un
  // MOTIF (abandon, repositionnement…) et déclare le retrait sans effacer.
  // Voir l'action « Sortir du portefeuille » ci-dessous.
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
        { name: 'date_releve', label: 'Date du relevé', labelEn: 'Survey date', type: 'date', aide: 'Date du PV de chantier, jamais la date de l’écran.' },
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
    {
      id: 'retrait',
      libelle: 'Sortir du portefeuille',
      libelleEn: 'Withdraw from portfolio',
      action: 'delete',
      avertissement:
        'Le serveur marque le projet « abandonné » et conserve la ligne avec votre motif : aucune opération n’est effacée de l’historique.',
      avertissementEn:
        'The server marks the project “abandoned” and keeps the line with your reason: no operation is erased from history.',
      champs: [
        { name: 'motif', label: 'Motif du retrait', labelEn: 'Withdrawal reason', type: 'texte', requisCreation: true, large: true, aide: 'Abandon, repositionnement, double emploi… Trois caractères au minimum, exigés par la route.' },
      ],
      executer: (id, v) => amenagementAPI.deleteProjet(id, { motif: req(v, 'motif') }),
      succes: 'Projet retiré de la programmation, motif enregistré.',
      succesEn: 'Project withdrawn from the programme, reason recorded.',
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

/* ════════════════════ 5. Titres domaniaux & occupations ════════════════════ */

export const registreTitres: ConfigRegistre = {
  permSousModule: 'titre_domanial',
  tcode: 'KAMT_DOM',
  icon: Stamp,
  titre: 'Titres domaniaux & occupations du domaine portuaire',
  titreEn: 'State domain titles & occupations',
  description:
    'Autorisations d’occuper, permissions d’exploiter, conventions d’occupation : bénéficiaire, assiette, redevance domaniale et échéances réelles.',
  descriptionEn:
    'Occupation permits, operating permissions and agreements: beneficiary, parcel, domain due and actual deadlines.',
  aide:
    'Accorder ou refuser un titre relève de l’autorité portuaire (et, pour le domaine national, de l’arrêté ministériel). Le module n’octroie rien : il enregistre le numéro de pièce, la décision écrite et ses dates.',
  aideEn:
    'Granting or refusing a title belongs to the port authority (and, for national domain, to the ministerial order). The module grants nothing: it records the document number, the written decision and its dates.',
  lister: (params) => amenagementAPI.listTitres(params),
  creer: (data) => amenagementAPI.createTitre(data),
  modifier: (id, data) => amenagementAPI.updateTitre(id, data),
  // Pas de retrait : un titre ne disparaît pas du registre, il arrive à
  // échéance ou est abrogé par un acte que l’on consigne.
  unicite: 'numero_piece',
  colonnes: [
    { name: 'numero_piece', label: 'N° de pièce', labelEn: 'Document no.', type: 'code', essence: true },
    { name: 'beneficiaire', label: 'Bénéficiaire', labelEn: 'Beneficiary', type: 'texte', essence: true },
    { name: 'type_titre', label: 'Nature du titre', labelEn: 'Title type', type: 'enum', nomenclature: 'type_titre_domanial' },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'place' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'enum', nomenclature: 'statut_titre_domanial', essence: true },
    { name: 'superficie_m2', label: 'Assiette', labelEn: 'Parcel area', type: 'nombre', unite: 'm²' },
    { name: 'redevance_annuelle_xaf', label: 'Redevance annuelle', labelEn: 'Annual due', type: 'montant' },
    { name: 'date_effet', label: 'Effet', labelEn: 'Effective', type: 'date' },
    { name: 'date_expiration', label: 'Expiration', labelEn: 'Expiry', type: 'date', essence: true },
    { name: 'renouvelable', label: 'Renouvelable', labelEn: 'Renewable', type: 'booleen' },
    { name: 'autorite_emettrice', label: 'Autorité émettrice', labelEn: 'Issuing authority', type: 'texte' },
  ],
  champs: [
    { name: 'numero_piece', label: 'Numéro de la pièce', labelEn: 'Document number', type: 'texte', requisCreation: true, lectureSeuleEdition: true, aide: 'Numéro porté sur le titre lui-même ; le serveur refuse un doublon.' },
    { name: 'type_titre', label: 'Nature du titre', labelEn: 'Title type', type: 'select', nomenclature: 'type_titre_domanial', requisCreation: true },
    { name: 'beneficiaire', label: 'Bénéficiaire', labelEn: 'Beneficiary', type: 'texte', requisCreation: true, large: true },
    { name: 'port_id', label: 'Place portuaire', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'objet', label: 'Objet de l’occupation', labelEn: 'Purpose of occupation', type: 'zone', large: true },
    { name: 'assiette', label: 'Assiette désignée', labelEn: 'Parcel description', type: 'texte', large: true, aide: 'Bornes, parcelle, poste : la désignation du titre, pas un calcul de surface.' },
    { name: 'superficie_m2', label: 'Superficie', labelEn: 'Area', type: 'nombre', unite: 'm²', min: 0 },
    { name: 'destination', label: 'Destination prévue', labelEn: 'Intended use', type: 'texte' },
    { name: 'redevance_annuelle_xaf', label: 'Redevance domaniale annuelle', labelEn: 'Annual domain due', type: 'montant', aide: 'Montant fixé par le barème applicable, recopié du titre.' },
    { name: 'taux_redevance', label: 'Taux ou base de calcul', labelEn: 'Rate or basis', type: 'texte' },
    { name: 'date_demande', label: 'Date de la demande', labelEn: 'Application date', type: 'date' },
    { name: 'date_signature', label: 'Date de signature', labelEn: 'Signature date', type: 'date' },
    { name: 'date_effet', label: 'Date d’effet', labelEn: 'Effective date', type: 'date' },
    { name: 'date_expiration', label: 'Date d’expiration', labelEn: 'Expiry date', type: 'date' },
    { name: 'renouvelable', label: 'Renouvelable', labelEn: 'Renewable', type: 'booleen' },
    { name: 'delai_renouvellement_mois', label: 'Préavis de renouvellement', labelEn: 'Renewal notice', type: 'nombre', unite: 'mois', min: 0 },
    { name: 'autorite_emettrice', label: 'Autorité émettrice', labelEn: 'Issuing authority', type: 'texte' },
    { name: 'reference_deliberation', label: 'Référence de la délibération', labelEn: 'Board reference', type: 'texte' },
    { name: 'piece_jointe', label: 'Référence de la pièce jointe', labelEn: 'Attached document ref.', type: 'texte' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_titre_domanial' },
    { name: 'motif_refus', label: 'Motif du refus', labelEn: 'Refusal grounds', type: 'zone', large: true },
    { name: 'source_reference', label: 'Source de la saisie', labelEn: 'Entry source', type: 'texte' },
    { name: 'date_verification', label: 'Date de vérification', labelEn: 'Verification date', type: 'date' },
    { name: 'notes', label: 'Notes', labelEn: 'Notes', type: 'zone', large: true },
  ],
  filtres: [
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'beneficiaire', label: 'Bénéficiaire', labelEn: 'Beneficiary', type: 'texte' },
    {
      name: 'expire',
      label: 'Titres échus',
      labelEn: 'Expired titles',
      type: 'select',
      booleen: true,
      aide: 'Le serveur compare la date d’expiration au jour courant ; une date non enregistrée reste dans les titres valables.',
    },
  ],
  actions: [
    {
      id: 'decision',
      libelle: 'Consigner la décision',
      libelleEn: 'Record the decision',
      action: 'approve',
      avertissement:
        'Un refus doit être motivé : la route serveur le refuse sinon, parce que la décision de l’autorité portuaire doit être écrite et justifiée.',
      avertissementEn:
        'A refusal must be reasoned: the server route rejects it otherwise, because the port authority’s decision must be written and justified.',
      champs: [
        { name: 'accord', label: 'Décision', labelEn: 'Decision', type: 'booleen', requisCreation: true, aide: 'Oui = titre délivré, Non = demande rejetée.' },
        { name: 'date_decision', label: 'Date de la décision', labelEn: 'Decision date', type: 'date', requisCreation: true },
        { name: 'autorite_emettrice', label: 'Autorité qui statue', labelEn: 'Deciding authority', type: 'texte' },
        { name: 'reference_deliberation', label: 'Référence de la délibération', labelEn: 'Board reference', type: 'texte' },
        { name: 'motif_refus', label: 'Motif du refus', labelEn: 'Refusal grounds', type: 'zone', large: true },
      ],
      executer: (id, v) => amenagementAPI.deciderTitre(id, {
        accord: v.accord === 'oui',
        date_decision: req(v, 'date_decision'),
        autorite_emettrice: optStr(v, 'autorite_emettrice'),
        reference_deliberation: optStr(v, 'reference_deliberation'),
        motif_refus: optStr(v, 'motif_refus'),
      }),
      succes: 'Décision consignée ; le statut du titre en découle.',
      succesEn: 'Decision recorded; the title status follows it.',
    },
  ],
};

/* ══════════════════ 6. Concessions & contrats d'exploitation ═══════════════ */

export const registreConcessions: ConfigRegistre = {
  permSousModule: 'concession',
  tcode: 'KAMT_CCS',
  icon: FileSignature,
  titre: 'Concessions & contrats d’exploitation',
  titreEn: 'Concessions & operating contracts',
  description:
    'Concession, affermage, BOT/AOT : autorité concédante, concessionnaire, périmètre, capacités promises, redevances, investissements et biens reversibles.',
  descriptionEn:
    'Concession, lease, BOT/AOT: granting authority, concessionaire, perimeter, promised capacity, dues, investments and revertible assets.',
  aide:
    'Un contrat se signe hors du logiciel. On y enregistre les clauses telles qu’au texte : les investissements promis et réalisés restent deux montants saisis, et leur écart n’est calculé par le serveur que si les deux existent.',
  aideEn:
    'A contract is signed outside this software. Clauses are entered as written: promised and actual investments stay two recorded amounts, and the server computes the gap only when both exist.',
  lister: (params) => amenagementAPI.listConcessions(params),
  creer: (data) => amenagementAPI.createConcession(data),
  modifier: (id, data) => amenagementAPI.updateConcession(id, data),
  unicite: 'code_contrat',
  colonnes: [
    { name: 'code_contrat', label: 'Code', labelEn: 'Code', type: 'code', essence: true },
    { name: 'nom_contrat', label: 'Contrat', labelEn: 'Contract', type: 'texte', essence: true },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'place' },
    { name: 'type_contrat', label: 'Forme', labelEn: 'Form', type: 'enum', nomenclature: 'type_contrat' },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'enum', nomenclature: 'statut_contrat', essence: true },
    { name: 'concessionnaire', label: 'Concessionnaire', labelEn: 'Concessionaire', type: 'texte' },
    { name: 'superficie_concedee_ha', label: 'Superficie concédée', labelEn: 'Granted area', type: 'nombre', unite: 'ha' },
    { name: 'investissement_promis_xaf', label: 'Investissement promis', labelEn: 'Promised investment', type: 'montant' },
    { name: 'investissement_realise_xaf', label: 'Réalisé', labelEn: 'Actual investment', type: 'montant' },
    { name: 'date_effet', label: 'Effet', labelEn: 'Effective', type: 'date' },
    { name: 'date_echeance', label: 'Échéance', labelEn: 'End date', type: 'date', essence: true },
  ],
  champs: [
    { name: 'code_contrat', label: 'Code du contrat', labelEn: 'Contract code', type: 'texte', requisCreation: true, lectureSeuleEdition: true },
    { name: 'nom_contrat', label: 'Intitulé du contrat', labelEn: 'Contract title', type: 'texte', requisCreation: true, large: true },
    { name: 'port_id', label: 'Place portuaire', labelEn: 'Port place', type: 'select', depuisPlaces: true, requisCreation: true },
    { name: 'terminal_id', label: 'Terminal (id serveur)', labelEn: 'Terminal (server id)', type: 'nombre', min: 1, aide: 'Identifiant technique du terminal dans le référentiel national ; laissé vide, aucune hypothèse n’est faite.' },
    { name: 'type_contrat', label: 'Forme contractuelle', labelEn: 'Contract form', type: 'select', nomenclature: 'type_contrat', requisCreation: true },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_contrat' },
    { name: 'autorite_concedante', label: 'Autorité concédante', labelEn: 'Granting authority', type: 'texte', requisCreation: true },
    { name: 'concessionnaire', label: 'Concessionnaire', labelEn: 'Concessionaire', type: 'texte', requisCreation: true },
    { name: 'groupe_final', label: 'Groupe actionnaire final', labelEn: 'Ultimate group', type: 'texte' },
    { name: 'objet', label: 'Objet de la concession', labelEn: 'Purpose', type: 'zone', large: true },
    { name: 'perimetre', label: 'Périmètre concédé', labelEn: 'Granted perimeter', type: 'zone', large: true },
    { name: 'superficie_concedee_ha', label: 'Superficie concédée', labelEn: 'Granted area', type: 'nombre', unite: 'ha', min: 0 },
    { name: 'longueur_quai_ml', label: 'Longueur de quai', labelEn: 'Quay length', type: 'nombre', unite: 'm', min: 0 },
    { name: 'capacite_contractuelle', label: 'Capacité contractuelle', labelEn: 'Contractual capacity', type: 'texte', aide: 'Ex. « 300 000 EVP/an », telle qu’écrite au contrat.' },
    { name: 'date_effet', label: 'Date d’effet', labelEn: 'Effective date', type: 'date' },
    { name: 'date_echeance', label: 'Date d’échéance', labelEn: 'End date', type: 'date' },
    { name: 'duree_mois', label: 'Durée', labelEn: 'Duration', type: 'nombre', unite: 'mois', min: 0 },
    { name: 'investissement_promis_xaf', label: 'Investissement promis', labelEn: 'Promised investment', type: 'montant' },
    { name: 'investissement_realise_xaf', label: 'Investissement réalisé', labelEn: 'Actual investment', type: 'montant' },
    { name: 'redevance_concession_xaf', label: 'Redevance de concession', labelEn: 'Concession due', type: 'montant' },
    { name: 'redevance_par_unite', label: 'Redevance unitaire', labelEn: 'Unit due', type: 'montant' },
    { name: 'unite_redevance', label: 'Unité de la redevance', labelEn: 'Due unit', type: 'texte', aide: 'Ex. « par EVP », « par tonne », telle que la clause l’énonce.' },
    { name: 'clauses_revolution', label: 'Clauses de revue', labelEn: 'Review clauses', type: 'zone', large: true },
    { name: 'sanctions_contractuelles', label: 'Sanctions contractuelles', labelEn: 'Contractual penalties', type: 'zone', large: true },
    { name: 'biens_reversibles', label: 'Biens reversibles', labelEn: 'Revertible assets', type: 'zone', large: true, aide: 'Inventaire des biens qui reviennent à l’autorité concédante en fin de contrat.' },
    { name: 'reference_approbation', label: 'Référence de l’acte d’approbation', labelEn: 'Approval act reference', type: 'texte' },
    { name: 'date_approbation', label: 'Date d’approbation', labelEn: 'Approval date', type: 'date' },
    { name: 'arret_travail', label: 'Arrêt de travail constaté', labelEn: 'Work stoppage noted', type: 'booleen' },
    { name: 'source_reference', label: 'Source de la saisie', labelEn: 'Entry source', type: 'texte' },
    { name: 'date_verification', label: 'Date de vérification', labelEn: 'Verification date', type: 'date' },
    { name: 'notes', label: 'Notes', labelEn: 'Notes', type: 'zone', large: true },
  ],
  filtres: [
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'statut', label: 'Statut', labelEn: 'Status', type: 'select', nomenclature: 'statut_contrat' },
  ],
  sondes: [
    {
      id: 'obligations',
      libelle: 'Écarts d’investissement',
      libelleEn: 'Investment gap',
      action: 'read',
      interroger: (id) => amenagementAPI.getObligationsConcession(id),
      cles: [
        { name: 'investissement_promis_xaf', label: 'Promis au contrat', labelEn: 'Promised in contract', type: 'montant' },
        { name: 'investissement_realise_xaf', label: 'Réalisé constaté', labelEn: 'Actual spend', type: 'montant' },
        { name: 'ecart_xaf', label: 'Écart (calcul serveur)', labelEn: 'Gap (server computation)', type: 'montant' },
        { name: 'respect_pct', label: 'Taux de respect', labelEn: 'Compliance rate', type: 'nombre', unite: '%' },
        { name: 'exploit_calculable', label: 'Comparaison possible', labelEn: 'Comparison available', type: 'booleen' },
        { name: 'date_echeance', label: 'Échéance du contrat', labelEn: 'Contract end date', type: 'date' },
      ],
      note: 'Un écart affiché « non enregistré » signifie qu’un des deux montants n’a jamais été saisi depuis une pièce contractuelle : le serveur refuse toute estimation.',
      noteEn: 'A gap shown as “not recorded” means one of the two amounts was never entered from a contractual document: the server refuses any estimate.',
    },
  ],
  circuits: [
    {
      libelle: 'Prononcé de la reversaison des biens',
      libelleEn: 'Reversion of the assets',
      motif:
        'La reversaison est un acte juridique de l’autorité concédante, constaté par procès-verbal et évaluation des biens : aucun connecteur officiel n’existe, le module ne la simule pas.',
      motifEn:
        'Reversion is a legal act of the granting authority, established by minutes and asset valuation: no official connector exists, the module does not simulate it.',
      interroger: (id) => amenagementAPI.prononcerReversaison(id),
    },
  ],
};

/* ═══════════════════ 7. Inventaire des infrastructures ═════════════════════ */

export const registreInfrastructures: ConfigRegistre = {
  permSousModule: 'infrastructure',
  tcode: 'KAMT_INF',
  icon: Building2,
  titre: 'Inventaire technique des infrastructures aménagées',
  titreEn: 'Technical inventory of developed infrastructure',
  description:
    'Ouvrages du domaine : quais, terre-pleins, plateformes, bâtiments. Géométrie relevée, état structurel, inspection et valeur patrimoniale tels qu’aux documents.',
  descriptionEn:
    'Domain structures: quays, aprons, platforms, buildings. Surveyed geometry, structural state, inspection and patrimonial value as documented.',
  aide:
    'Aucune note de génie civil n’est déduite ici : elle provient d’un rapport d’expertise. Un ouvrage sans date d’inspection enregistrée reste compté « non inspecté » dans la synthèse du département.',
  aideEn:
    'No civil-engineering score is inferred here: it comes from an expert report. A structure with no recorded inspection date stays counted as “not inspected” in the department synthesis.',
  lister: (params) => amenagementAPI.listInfrastructures(params),
  creer: (data) => amenagementAPI.createInfrastructure(data),
  modifier: (id, data) => amenagementAPI.updateInfrastructure(id, data),
  unicite: 'code',
  colonnes: [
    { name: 'code', label: 'Code', labelEn: 'Code', type: 'code', essence: true },
    { name: 'designation', label: 'Ouvrage', labelEn: 'Structure', type: 'texte', essence: true },
    { name: 'type_infrastructure', label: 'Nature', labelEn: 'Type', type: 'enum', nomenclature: 'type_infrastructure' },
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'place' },
    { name: 'statut', label: 'État', labelEn: 'Condition', type: 'enum', nomenclature: 'etat_infrastructure', essence: true },
    { name: 'longueur_ml', label: 'Longueur', labelEn: 'Length', type: 'nombre', unite: 'm' },
    { name: 'superficie_m2', label: 'Superficie', labelEn: 'Area', type: 'nombre', unite: 'm²' },
    { name: 'profondeur_utile_m', label: 'Profondeur utile', labelEn: 'Useful depth', type: 'nombre', unite: 'm' },
    { name: 'date_mise_service', label: 'Mise en service', labelEn: 'Commissioned', type: 'date' },
    { name: 'date_derniere_inspection', label: 'Dernière inspection', labelEn: 'Last inspection', type: 'date' },
    { name: 'note_genie_civil', label: 'Note', labelEn: 'Score', type: 'nombre', unite: '/100' },
    { name: 'reversable', label: 'Reversible', labelEn: 'Revertible', type: 'booleen' },
  ],
  champs: [
    { name: 'code', label: 'Code de l’ouvrage', labelEn: 'Structure code', type: 'texte', requisCreation: true, lectureSeuleEdition: true },
    { name: 'designation', label: 'Désignation', labelEn: 'Designation', type: 'texte', requisCreation: true, large: true },
    { name: 'type_infrastructure', label: 'Nature de l’ouvrage', labelEn: 'Structure type', type: 'select', nomenclature: 'type_infrastructure', requisCreation: true },
    { name: 'port_id', label: 'Place portuaire', labelEn: 'Port place', type: 'select', depuisPlaces: true, requisCreation: true },
    { name: 'terminal_id', label: 'Terminal (id serveur)', labelEn: 'Terminal (server id)', type: 'nombre', min: 1 },
    { name: 'projet_id', label: 'Projet d’origine (id serveur)', labelEn: 'Origin project (server id)', type: 'nombre', min: 1 },
    { name: 'zone_id', label: 'Zone portuaire (id serveur)', labelEn: 'Port zone (server id)', type: 'nombre', min: 1 },
    { name: 'emplacement', label: 'Emplacement', labelEn: 'Location', type: 'texte', large: true },
    { name: 'statut', label: 'État de l’ouvrage', labelEn: 'Condition', type: 'select', nomenclature: 'etat_infrastructure' },
    { name: 'longueur_ml', label: 'Longueur', labelEn: 'Length', type: 'nombre', unite: 'm', min: 0 },
    { name: 'largeur_m', label: 'Largeur', labelEn: 'Width', type: 'nombre', unite: 'm', min: 0 },
    { name: 'superficie_m2', label: 'Superficie', labelEn: 'Area', type: 'nombre', unite: 'm²', min: 0 },
    { name: 'profondeur_utile_m', label: 'Profondeur utile', labelEn: 'Useful depth', type: 'nombre', unite: 'm', min: 0 },
    { name: 'hauteur_parement_m', label: 'Hauteur de parement', labelEn: 'Facing height', type: 'nombre', unite: 'm', min: 0 },
    { name: 'portance_tonnes_m2', label: 'Portance du terre-plein', labelEn: 'Apron bearing capacity', type: 'nombre', min: 0 },
    { name: 'capacite_teus', label: 'Capacité', labelEn: 'Capacity', type: 'nombre', unite: 'EVP', min: 0 },
    { name: 'date_mise_service', label: 'Date de mise en service', labelEn: 'Commissioning date', type: 'date' },
    { name: 'date_derniere_inspection', label: 'Date de la dernière inspection', labelEn: 'Last inspection date', type: 'date' },
    { name: 'periodicite_inspection_mois', label: 'Périodicité d’inspection', labelEn: 'Inspection interval', type: 'nombre', unite: 'mois', min: 0 },
    { name: 'prochaine_inspection', label: 'Prochaine inspection', labelEn: 'Next inspection', type: 'date' },
    { name: 'etat_structural', label: 'Appréciation structurelle', labelEn: 'Structural assessment', type: 'texte', aide: 'Terme du rapport d’expertise ; le serveur le normalise en majuscules sans en inventer.' },
    { name: 'note_genie_civil', label: 'Note de génie civil', labelEn: 'Civil engineering score', type: 'nombre', min: 0, max: 100, aide: 'Note issue d’une expertise, jamais calculée par le logiciel.' },
    { name: 'travaux_renovation_prevus', label: 'Travaux de rénovation prévus', labelEn: 'Planned renovation', type: 'booleen' },
    { name: 'estimation_renovation_xaf', label: 'Estimation de rénovation', labelEn: 'Renovation estimate', type: 'montant' },
    { name: 'valeur_patrimoniale_xaf', label: 'Valeur patrimoniale', labelEn: 'Patrimonial value', type: 'montant' },
    { name: 'date_entree_patrimoine', label: 'Entrée au patrimoine', labelEn: 'Entry in assets register', type: 'date' },
    { name: 'regime_fiscal', label: 'Régime fiscal', labelEn: 'Tax regime', type: 'texte' },
    { name: 'reversable', label: 'Bien reversible', labelEn: 'Revertible asset', type: 'booleen' },
    { name: 'operateur_entretien', label: 'Opérateur chargé de l’entretien', labelEn: 'Maintenance operator', type: 'texte' },
    { name: 'sources_documents', label: 'Documents sources', labelEn: 'Source documents', type: 'liste', large: true },
    { name: 'source_reference', label: 'Source de la saisie', labelEn: 'Entry source', type: 'texte' },
    { name: 'date_verification', label: 'Date de vérification', labelEn: 'Verification date', type: 'date' },
    { name: 'notes', label: 'Notes', labelEn: 'Notes', type: 'zone', large: true },
  ],
  filtres: [
    { name: 'port_id', label: 'Place', labelEn: 'Port place', type: 'select', depuisPlaces: true },
    { name: 'statut', label: 'État', labelEn: 'Condition', type: 'select', nomenclature: 'etat_infrastructure' },
    { name: 'type_infrastructure', label: 'Nature', labelEn: 'Type', type: 'select', nomenclature: 'type_infrastructure' },
  ],
  actions: [
    {
      id: 'inspection',
      libelle: 'Enregistrer une inspection',
      libelleEn: 'Record an inspection',
      action: 'modify',
      avertissement:
        'La date du rapport et la note viennent de l’expertise réelle : laisser un champ vide ne le remplit pas automatiquement.',
      avertissementEn:
        'The report date and the score come from the actual expertise: leaving a field blank does not fill it.',
      champs: [
        { name: 'date_inspection', label: 'Date du rapport de visite', labelEn: 'Report date', type: 'date', requisCreation: true },
        { name: 'etat_structural', label: 'Appréciation structurelle', labelEn: 'Structural assessment', type: 'texte' },
        { name: 'note_genie_civil', label: 'Note (0 à 100)', labelEn: 'Score (0 to 100)', type: 'nombre', min: 0, max: 100 },
        { name: 'prochaine_inspection', label: 'Prochaine inspection', labelEn: 'Next inspection', type: 'date' },
      ],
      executer: (id, v) => amenagementAPI.consignerInspection(id, {
        date_inspection: req(v, 'date_inspection'),
        etat_structural: optStr(v, 'etat_structural'),
        note_genie_civil: optNum(v, 'note_genie_civil'),
        prochaine_inspection: optStr(v, 'prochaine_inspection'),
      }),
      succes: 'Relevé d’inspection enregistré sur la fiche de l’ouvrage.',
      succesEn: 'Inspection survey recorded on the structure sheet.',
    },
    {
      id: 'retrait',
      libelle: 'Sortir de l’inventaire',
      libelleEn: 'Remove from inventory',
      action: 'delete',
      avertissement:
        'Le motif est exigé par le serveur : un ouvrage démoli est marqué « démoli », un ouvrage sorti du patrimoine garde sa fiche avec la mention de retrait.',
      avertissementEn:
        'The server requires a reason: a demolished structure is marked “demolished”, one leaving the assets register keeps its sheet with the withdrawal note.',
      champs: [
        { name: 'motif', label: 'Motif du retrait', labelEn: 'Withdrawal reason', type: 'texte', requisCreation: true, large: true, aide: 'Démolition, sortie de patrimoine, erreur de saisie…' },
      ],
      executer: (id, v) => amenagementAPI.deleteInfrastructure(id, { motif: req(v, 'motif') }),
      succes: 'Ouvrage sorti de l’inventaire actif, motif consigné.',
      succesEn: 'Structure removed from the active inventory, reason recorded.',
    },
  ],
};
