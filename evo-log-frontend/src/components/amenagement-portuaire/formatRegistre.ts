/**
 * Formatage des cellules des registres d'aménagement portuaire.
 *
 * Règle commune avec le backend : une donnée absente ne devient JAMAIS un
 * zéro, une date du jour ou une estimation. Elle reste vide et s'affiche
 * comme telle, pour qu'un agent ne prenne pas un manquant pour un chiffre.
 */
import type {
  ChampRegistre,
  CleSonde,
  ColonneRegistre,
  LigneRegistre,
  Nomenclatures,
  PlacePortuaire,
  ValeurCellule,
} from './typesRegistre';

/** Libellé d'un manquant. Volontairement neutre : « à saisir », pas « 0 ». */
export const MANQUANT_FR = 'non enregistré';
export const MANQUANT_EN = 'not recorded';

export function tManquant(lang: 'fr' | 'en'): string {
  return lang === 'en' ? MANQUANT_EN : MANQUANT_FR;
}

/** Les valeurs d'enum côté serveur sont en snake_case (« schema_directeur ») :
 *  on les rend lisibles sans inventer de nouveau vocabulaire. */
export function humaniser(valeur: string): string {
  return valeur.replace(/[_-]+/g, ' ').trim();
}

const FORMAT_NOMBRE = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });
const FORMAT_MONTANT = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });

export function estAbsent(v: ValeurCellule): boolean {
  if (v === null || v === undefined) return true;
  if (typeof v === 'string') return v.trim() === '';
  if (Array.isArray(v)) return v.length === 0;
  return false;
}

/** Date ISO (YYYY-MM-DD ou datetime) en JJ/MM/AAAA. Une date absente reste
 *  un manquant : aucune valeur de repli n'est injectée. */
export function formaterDate(iso: string, lang: 'fr' | 'en'): string {
  const brut = String(iso).slice(0, 10);
  const d = new Date(`${brut}T00:00:00`);
  if (Number.isNaN(d.getTime())) return brut;
  return lang === 'en'
    ? d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    : d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

/** Un montant FCFA, ou le libellé « non enregistré » si la saisie manque. */
export function formaterMontant(v: ValeurCellule, lang: 'fr' | 'en'): string {
  if (estAbsent(v) || typeof v !== 'number') return tManquant(lang);
  return `${FORMAT_MONTANT.format(v)} FCFA`;
}

/** Traduit une valeur d'enum avec la nomenclature SERVEUR (clé `valeur`), et
 *  retombe sur la valeur brute humanisée si le serveur ne la connaît pas —
 *  le cas échéant c'est une donnée saisie hors cadre, on l'affiche telle quelle. */
export function libelleEnum(
  valeur: ValeurCellule,
  cle: string | undefined,
  nomenclatures: Nomenclatures | null,
): string | null {
  if (estAbsent(valeur) || typeof valeur !== 'string') return null;
  const entrees = cle && nomenclatures ? nomenclatures[cle] : undefined;
  const trouvee = entrees?.find((e) => e.valeur === valeur || e.code === valeur);
  return trouvee ? humaniser(trouvee.valeur) : humaniser(valeur);
}

/** Rend une cellule prête à afficher ; `manquant` signale une donnée absente. */
export function rendreCellule(
  colonne: ColonneRegistre,
  ligne: LigneRegistre,
  lang: 'fr' | 'en',
  nomenclatures: Nomenclatures | null,
  places: PlacePortuaire[] = [],
): { texte: string; manquant: boolean } {
  const v = ligne[colonne.name];
  switch (colonne.type) {
    case 'montant':
      return { texte: formaterMontant(v, lang), manquant: estAbsent(v) };
    case 'nombre':
      if (estAbsent(v)) return { texte: tManquant(lang), manquant: true };
      return { texte: `${FORMAT_NOMBRE.format(Number(v))}${colonne.unite ? ` ${colonne.unite}` : ''}`, manquant: false };
    case 'date': {
      if (estAbsent(v)) return { texte: tManquant(lang), manquant: true };
      return { texte: formaterDate(String(v), lang), manquant: false };
    }
    case 'booleen': {
      if (v === true) return { texte: lang === 'en' ? 'Yes' : 'Oui', manquant: false };
      if (v === false) return { texte: lang === 'en' ? 'No' : 'Non', manquant: false };
      return { texte: tManquant(lang), manquant: true };
    }
    case 'enum': {
      const lib = libelleEnum(v, colonne.nomenclature, nomenclatures);
      if (lib === null) return { texte: tManquant(lang), manquant: true };
      return { texte: lib, manquant: false };
    }
    case 'liste': {
      if (!Array.isArray(v) || v.length === 0) return { texte: tManquant(lang), manquant: true };
      return { texte: v.map(String).join(' · '), manquant: false };
    }
    case 'place': {
      // port_id → nom servi par /places. Une place absente du référentiel
      // national reste un manquant : on n'invente ni nom ni code.
      if (estAbsent(v)) return { texte: tManquant(lang), manquant: true };
      const place = places.find((p) => p.id === Number(v));
      if (!place) return { texte: `#${v}`, manquant: true };
      return { texte: place.nom || place.code, manquant: false };
    }
    default: {
      if (estAbsent(v)) return { texte: tManquant(lang), manquant: true };
      const brut = Array.isArray(v) ? v.map(String).join(' · ') : String(v);
      return { texte: `${brut}${colonne.unite && colonne.type !== 'code' ? ` ${colonne.unite}` : ''}`, manquant: false };
    }
  }
}

/** Rend une clé de la réponse d'une sonde : un agrégat SERVEUR, jamais un
 *  calcul fait ici. `null` (non calculable faute de saisie) reste un manquant. */
export function rendreCleSonde(
  cle: CleSonde,
  brut: unknown,
  lang: 'fr' | 'en',
): { texte: string; manquant: boolean } {
  if (brut === null || brut === undefined || (typeof brut === 'string' && brut.trim() === '')) {
    return { texte: tManquant(lang), manquant: true };
  }
  switch (cle.type) {
    case 'montant':
      return typeof brut === 'number'
        ? { texte: `${FORMAT_MONTANT.format(brut)} FCFA`, manquant: false }
        : { texte: tManquant(lang), manquant: true };
    case 'nombre':
      if (typeof brut !== 'number') return { texte: String(brut), manquant: false };
      return { texte: `${FORMAT_NOMBRE.format(brut)}${cle.unite ? ` ${cle.unite}` : ''}`, manquant: false };
    case 'booleen':
      if (brut === true) return { texte: lang === 'en' ? 'Yes' : 'Oui', manquant: false };
      if (brut === false) return { texte: lang === 'en' ? 'No' : 'Non', manquant: false };
      return { texte: String(brut), manquant: false };
    case 'date':
      return { texte: formaterDate(String(brut), lang), manquant: false };
    default:
      return { texte: typeof brut === 'object' ? JSON.stringify(brut) : String(brut), manquant: false };
  }
}

/** Valeur d'un champ pour pré-remplir le formulaire d'édition. Une date
 *  datetime serveur est tronquée au jour pour <input type="date">. */
export function valeurSaisie(v: ValeurCellule): string {
  if (v === null || v === undefined) return '';
  if (Array.isArray(v)) return v.map(String).join('\n');
  return String(v);
}

/** Le champ est-il vide au sens métier (donc non transmis au serveur) ? */
export function saisieVide(val: string): boolean {
  return val.trim() === '';
}

/** Libellé d'un champ selon la langue active. */
export function labelChamp(c: ChampRegistre, lang: 'fr' | 'en'): string {
  return lang === 'en' && c.labelEn ? c.labelEn : c.label;
}

export function labelColonne(c: ColonneRegistre, lang: 'fr' | 'en'): string {
  return lang === 'en' && c.labelEn ? c.labelEn : c.label;
}

export function aideChamp(c: ChampRegistre, lang: 'fr' | 'en'): string | undefined {
  if (lang !== 'en') return c.aide;
  return c.aideEn || c.aide;
}
