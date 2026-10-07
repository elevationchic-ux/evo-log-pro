/**
 * Contrats generiques du chassis RegistreGenerique.
 *
 * Derive du pattern amenagement-portuaire (typesRegistre.ts) mais rendu
 * independant de tout module specifique :
 *  - `permModule` remplace le prefixe code en dur "amenagement" ;
 *  - `fetchNomenclatures` et `fetchReferentiels` sont des callbacks declares
 *    dans la config, pas des appels a une API particuliere ;
 *  - les places portuaires (specifiques a amenagement) restent supportees
 *    optionnellement via le champ `referentiels`.
 *
 * Principe d'honnetete :
 *  - une valeur absente reste null et s'affiche "non enregistre" ;
 *  - aucun choix n'est fige : les options viennent de l'API ;
 *  - les champs sont la description exacte des schemas Pydantic backend.
 */
import type { AxiosResponse } from 'axios';
import type { LucideIcon } from 'lucide-react';

/** Une cellule telle que la sert l'API. */
export type ValeurCellule =
  | string
  | number
  | boolean
  | null
  | undefined
  | string[]
  | Record<string, unknown>[];

/** Une ligne de registre. `id` est la cle primaire serveur. */
export type LigneRegistre = { id: number } & Record<string, ValeurCellule>;

/** Payload d'ecriture : seules les cles saisies sont envoyees. */
export type ChargementRegistre = Record<string, string | number | boolean | string[] | null>;

export type TypeChamp =
  | 'texte'
  | 'zone'
  | 'nombre'
  | 'montant'
  | 'date'
  | 'booleen'
  | 'select'
  | 'liste';

export interface ChampRegistre {
  /** Nom EXACT du champ dans le schema Pydantic backend. */
  name: string;
  label: string;
  labelEn?: string;
  type: TypeChamp;
  requisCreation?: boolean;
  lectureSeuleEdition?: boolean;
  /** Cle de la nomenclature serveur (ex. 'statut_schema'). */
  nomenclature?: string;
  /** Options prises depuis un referentiel externe (ex. places portuaires). */
  depuisReferentiel?: string;
  min?: number;
  max?: number;
  pas?: number;
  unite?: string;
  large?: boolean;
  aide?: string;
  aideEn?: string;
}

export type TypeColonne =
  | 'code'
  | 'texte'
  | 'nombre'
  | 'montant'
  | 'date'
  | 'booleen'
  | 'enum'
  | 'liste'
  | 'place'
  | 'largeur';

export interface ColonneRegistre {
  name: string;
  label: string;
  labelEn?: string;
  type?: TypeColonne;
  nomenclature?: string;
  unite?: string;
  essence?: boolean;
}

export interface FiltreRegistre {
  name: string;
  label: string;
  labelEn?: string;
  type: 'select' | 'date' | 'texte' | 'nombre';
  nomenclature?: string;
  depuisReferentiel?: string;
  booleen?: boolean;
  aide?: string;
  aideEn?: string;
}

/** Action metier en une ligne (POST …/{id}/… avec des parametres). */
export interface ActionRegistre {
  id: string;
  libelle: string;
  libelleEn?: string;
  action: 'create' | 'modify' | 'approve' | 'read' | 'export' | 'delete';
  champs: ChampRegistre[];
  executer: (id: number, valeurs: ChargementRegistre) => Promise<AxiosResponse>;
  succes: string;
  succesEn?: string;
  avertissement?: string;
  avertissementEn?: string;
}

/** Teleprocedure institutionnelle : la route existe et repond 501. */
export interface CircuitExterne {
  libelle: string;
  libelleEn?: string;
  motif: string;
  motifEn?: string;
  interroger: (id: number) => Promise<AxiosResponse>;
}

export interface CleSonde {
  name: string;
  label: string;
  labelEn?: string;
  type?: 'montant' | 'nombre' | 'booleen' | 'date' | 'texte';
  unite?: string;
}

export interface SondeServeur {
  id: string;
  libelle: string;
  libelleEn?: string;
  action?: 'read' | 'modify' | 'approve';
  interroger: (id: number) => Promise<AxiosResponse>;
  cles: CleSonde[];
  note?: string;
  noteEn?: string;
}

/** Reponse de /nomenclatures : { cle: [{ code, valeur }] }. */
export type Nomenclatures = Record<string, { code: string; valeur: string }[]>;

/** Element d'un referentiel generique (places, zones, etc.). */
export interface ReferentielItem {
  id: number;
  code?: string;
  nom?: string | null;
  est_actif?: boolean;
  [key: string]: unknown;
}

export interface ConfigRegistre {
  /** Prefixe de permission backend (ex. 'amenagement', 'port_ops', 'transit'). */
  permModule: string;
  /** Sous-module dans le catalogue de permissions. */
  permSousModule: string;
  tcode: string;
  icon: LucideIcon;
  titre: string;
  titreEn: string;
  description: string;
  descriptionEn: string;
  aide: string;
  aideEn: string;
  lister: (params: Record<string, string | number | boolean>) => Promise<AxiosResponse>;
  creer: (data: ChargementRegistre) => Promise<AxiosResponse>;
  modifier: (id: number, data: ChargementRegistre) => Promise<AxiosResponse>;
  colonnes: ColonneRegistre[];
  champs: ChampRegistre[];
  filtres?: FiltreRegistre[];
  actions?: ActionRegistre[];
  sondes?: SondeServeur[];
  circuits?: CircuitExterne[];
  unicite?: string;
  /** Callback pour recuperer les nomenclatures de ce module. */
  fetchNomenclatures?: () => Promise<AxiosResponse>;
  /** Referentiels externes optionnels (places portuaires, etc.). */
  referentiels?: Record<string, () => Promise<AxiosResponse>>;
}
