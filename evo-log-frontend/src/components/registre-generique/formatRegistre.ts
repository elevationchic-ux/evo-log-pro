/**
 * Formatage des cellules du RegistreGenerique.
 *
 * Reexporte la logique identique a formatRegistre.ts (amenagement) mais
 * generalisee : le type `place` de colonne resout via le champ generique
 * `referentiels` plutot que la liste `PlacePortuaire` specifique.
 */
import type {
  ChampRegistre,
  CleSonde,
  ColonneRegistre,
  LigneRegistre,
  Nomenclatures,
  ReferentielItem,
  ValeurCellule,
} from './typesRegistre';

export const MANQUANT_FR = 'non enregistré';
export const MANQUANT_EN = 'not recorded';

export function tManquant(lang: 'fr' | 'en'): string {
  return lang === 'en' ? MANQUANT_EN : MANQUANT_FR;
}

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

export function formaterDate(iso: string, lang: 'fr' | 'en'): string {
  const brut = String(iso).slice(0, 10);
  const d = new Date(`${brut}T00:00:00`);
  if (Number.isNaN(d.getTime())) return brut;
  return lang === 'en'
    ? d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    : d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

export function formaterMontant(v: ValeurCellule, lang: 'fr' | 'en'): string {
  if (estAbsent(v) || typeof v !== 'number') return tManquant(lang);
  return `${FORMAT_MONTANT.format(v)} FCFA`;
}

export function formaterMesure(v: ValeurCellule, unite: string, lang: 'fr' | 'en'): string {
  if (estAbsent(v) || typeof v !== 'number') return tManquant(lang);
  return `${FORMAT_NOMBRE.format(v)} ${unite}`;
}

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

/** Rend une cellule prete a afficher. `referentiels` optionnel resout les
 *  colonnes de type 'place' via un referentiel generique. */
export function rendreCellule(
  colonne: ColonneRegistre,
  ligne: LigneRegistre,
  lang: 'fr' | 'en',
  nomenclatures: Nomenclatures | null,
  referentiels?: Record<string, ReferentielItem[]>,
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
      return { texte: v.map(String).join(' \u00b7 '), manquant: false };
    }
    case 'place': {
      if (estAbsent(v)) return { texte: tManquant(lang), manquant: true };
      // Resout depuis le premier referentiel disponible (places, zones, etc.)
      const items = referentiels ? Object.values(referentiels).flat() : [];
      const found = items.find((p) => p.id === Number(v));
      if (!found) return { texte: `#${v}`, manquant: true };
      return { texte: (found.nom || found.code || `#${v}`) as string, manquant: false };
    }
    default: {
      if (estAbsent(v)) return { texte: tManquant(lang), manquant: true };
      const brut = Array.isArray(v) ? v.map(String).join(' \u00b7 ') : String(v);
      return { texte: `${brut}${colonne.unite && colonne.type !== 'code' ? ` ${colonne.unite}` : ''}`, manquant: false };
    }
  }
}

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

export function valeurSaisie(v: ValeurCellule): string {
  if (v === null || v === undefined) return '';
  if (Array.isArray(v)) return v.map(String).join('\n');
  return String(v);
}

export function saisieVide(val: string): boolean {
  return val.trim() === '';
}

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
