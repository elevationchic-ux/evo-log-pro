// Générateur éphémère des pages de registre du département Aménagement
// portuaire : une page fine par segment d'URL, toutes identiques sauf le
// document d'en-tête, le nom du composant et le registre monté.
const fs = require('fs');
const path = require('path');

const base = path.join(__dirname, '..', 'src', 'app', '(app)', 'amenagement-portuaire');

const pages = [
  {
    segment: 'programmation',
    comp: 'AmenagementPortuaireProgrammationPage',
    config: 'registreProgrammation',
    doc: [
      'Chaîne de programmation des projets (fiche technique, PIP/CDMT, engagement).',
      'Les états affichés viennent de la nomenclature « statut_document_programmation »',
      'servie par /nomenclatures : la page n\u2019en fixe aucun. Les visas (maturité,',
      'contrôle financier) sont consignés comme actes pris par l\u2019administration.',
    ],
  },
  {
    segment: 'marches',
    comp: 'AmenagementPortuaireMarchesPage',
    config: 'registreMarches',
    doc: [
      'Marchés publics d\u2019aménagement & contrats de PPP.',
      'Le logiciel tient la trace des pièces (DAO, avis COLIFE ou CIP, attribution,',
      'réceptions) : il ne conduit aucune procédure de passation, et la route de',
      'soumission à la COLIFE le dit elle-même (501).',
    ],
  },
  {
    segment: 'titres-domaniaux',
    comp: 'AmenagementPortuaireTitresDomaniauxPage',
    config: 'registreTitres',
    doc: [
      'Titres domaniaux & occupations du domaine public.',
      'Une décision (accord ou refus motivé) est enregistrée avec son autorité et sa',
      'date réelles. Un titre n\u2019est jamais effacé : abrogé, annulé ou échu, il reste',
      'au registre, qui fait foi.',
    ],
  },
  {
    segment: 'concessions',
    comp: 'AmenagementPortuaireConcessionsPage',
    config: 'registreConcessions',
    doc: [
      'Concessions & contrats d\u2019exploitation.',
      'L\u2019écart entre investissements promis et réalisés n\u2019est pas calculé dans le',
      'navigateur : la sonde « Obligations » relit /concessions/{id}/obligations et',
      'affiche les agrégats du serveur, y compris leurs blanks quand rien n\u2019est saisi.',
    ],
  },
  {
    segment: 'infrastructures',
    comp: 'AmenagementPortuaireInfrastructuresPage',
    config: 'registreInfrastructures',
    doc: [
      'Inventaire technique des infrastructures aménagées.',
      'Aucune note de génie civil n\u2019est déduite : elle provient d\u2019un rapport',
      'd\u2019expertise consigné par l\u2019action dédiée. Une sortie d\u2019inventaire exige un',
      'motif, la route DELETE du serveur le refusant sinon.',
    ],
  },
  {
    segment: 'dragage',
    comp: 'AmenagementPortuaireDragagePage',
    config: 'registreDragage',
    doc: [
      'Campagnes de dragage & profondeurs du chenal.',
      'Volumes mesuré et facturé restent deux colonnes distinctes : la réconciliation',
      'appartient au décompte de l\u2019ingénieur. Le statut est une saisie libre, le',
      'serveur ne publie pas de vocabulaire pour cette colonne.',
    ],
  },
  {
    segment: 'autorisations',
    comp: 'AmenagementPortuaireAutorisationsPage',
    config: 'registreAutorisations',
    doc: [
      'Autorisations administratives & études d\u2019impact (EIES, permis).',
      'Les natures et statuts proposés viennent de /nomenclatures. Le dépôt auprès du',
      'guichet environnemental officiel n\u2019est pas simulé : la route l\u2019annonce (501),',
      'la page affiche le message du serveur tel quel.',
    ],
  },
];

const entete = (doc) => doc.map((l) => ` * ${l}`).join('\n');

for (const p of pages) {
  const contenu = `'use client';

/**
${entete(p.doc)}
 *
 * Page fine : toute la mécanique (permissions granulaires, référentiels serveurs,
 * champs vides non envoyés, erreurs 409/422/501 remontées telles quelles) est
 * portée par le châssis commun RegistrePortuaire.
 */
import RegistrePortuaire from '@/components/amenagement-portuaire/RegistrePortuaire';
import { ${p.config} } from '@/components/amenagement-portuaire/registres';

export default function ${p.comp}() {
  return <RegistrePortuaire config={${p.config}} />;
}
`;
  const dossier = path.join(base, p.segment);
  fs.mkdirSync(dossier, { recursive: true });
  fs.writeFileSync(path.join(dossier, 'page.tsx'), contenu, { encoding: 'utf8' });
  console.log('écrit', path.relative(process.cwd(), path.join(dossier, 'page.tsx')));
}
