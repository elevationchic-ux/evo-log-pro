/**
 * Contrats du département Aménagement portuaire côté frontend.
 *
 * Principe d'honnêteté (aligné sur le router backend
 * /api/v1/amenagement-portuaire) :
 *  - aucune donnée métier n'est codée en dur ici : les vocabulaires d'écrans
 *    viennent de `/nomenclatures`, les places portuaires de `/places`, les
 *    agrégats de `/synthese` ;
 *  - une valeur absente reste `null` et s'affiche « non enregistré » — jamais
 *    0, jamais une date du jour, jamais une estimation ;
 *  - les champs ci-dessous ne sont que la DESCRIPTION de ce que le serveur
 *    accepte (schemas Pydantic de app/schemas/amenagement_portuaire.py) : ils
 *    ne créent aucune colonne inventée.
 */
import type { AxiosResponse } from 'axios';
import type { LucideIcon } from 'lucide-react';

/** Une cellule telle que la sert l'API (les listes JSON restent des listes). */
export type ValeurCellule =
  | string
  | number
  | boolean
  | null
  | undefined
  | string[]
  | Record<string, unknown>[];

/** Une ligne de registre. `id` est la clé primaire serveur ; le reste est
 *  indexé par le nom exact du champ Pydantic, donc rien n'est deviné. */
export type LigneRegistre = { id: number } & Record<string, ValeurCellule>;

/** Payload d'écriture : seules les clés saisies sont envoyées
 *  (le backend fait `exclude_unset`, un champ absent n'écrase rien). */
export type ChargementRegistre = Record<string, string | number | boolean | string[] | null>;

export type TypeChamp =
  | 'texte'
  | 'zone'        // textarea
  | 'nombre'
  | 'montant'     // nombre + suffixe XAF à l'affichage
  | 'date'
  | 'booleen'
  | 'select'      // options servies par /nomenclatures ou /places
  | 'liste';      // liste de chaînes (saisie ligne par ligne)

export interface ChampRegistre {
  /** Nom EXACT du champ dans le schéma Pydantic backend. */
  name: string;
  label: string;
  labelEn?: string;
  type: TypeChamp;
  /** Requis à la création uniquement (le serveur valide aussi : ce drapeau
   *  sert à désactiver l'envoi, pas à remplacer la validation). */
  requisCreation?: boolean;
  /** Immuable après création : les références uniques (code, numéro d'arrêté)
   *  ne se rééditent pas, on corrige la ligne existante. */
  lectureSeuleEdition?: boolean;
  /** Clé de la nomenclature serveur (ex. 'statut_schema'). */
  nomenclature?: string;
  /** Options prises sur /places (référentiel national, jamais une liste figée). */
  depuisPlaces?: boolean;
  min?: number;
  max?: number;
  pas?: number;
  /** Unité rappelée dans le libellé (m, m², m³, EVP, mois…). Purement
   *  typographique : elle ne convertit ni n'arrondit la saisie. */
  unite?: string;
  /** Prend toute la largeur du formulaire. */
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
  /** port_id : résolu avec /places (référentiel national), jamais avec une
   *  table de noms codée en dur. */
  | 'place'
  | 'largeur';

export interface ColonneRegistre {
  name: string;
  label: string;
  labelEn?: string;
  type?: TypeColonne;
  /** Pour traduire une valeur d'enum avec la nomenclature serveur. */
  nomenclature?: string;
  /** Unité de mesure affichée seulement si la valeur existe (m, m², %…). */
  unite?: string;
  /** Prioritaire sur mobile : les premières colonnes restent visibles. */
  essence?: boolean;
}

export interface FiltreRegistre {
  /** Nom EXACT du paramètre de query backend. */
  name: string;
  label: string;
  labelEn?: string;
  type: 'select' | 'date' | 'texte' | 'nombre';
  nomenclature?: string;
  depuisPlaces?: boolean;
  /** Filtre booleéen : le serveur attend true/false, pas une chaîne libre. */
  booleen?: boolean;
  /** Ce que le serveur fait vraiment de ce paramètre — utile quand un filtre
   *  change le sens d'une liste (ex. « titres échus »). */
  aide?: string;
  aideEn?: string;
}

/** Action métier en un ligne (POST …/{id}/… avec des paramètres de query). */
export interface ActionRegistre {
  id: string;
  libelle: string;
  libelleEn?: string;
  /** Action du code de permission granulaire (amenagement.<sous-module>.<action>). */
  action: 'create' | 'modify' | 'approve' | 'read' | 'export' | 'delete';
  champs: ChampRegistre[];
  executer: (id: number, valeurs: ChargementRegistre) => Promise<AxiosResponse>;
  succes: string;
  succesEn?: string;
  /** Rappel pédagogique : l'écran enregistre un acte pris ailleurs, il ne le
   *  prend pas. Affiché au-dessus du formulaire. */
  avertissement?: string;
  avertissementEn?: string;
}

/** Téléprocédure institutionnelle : la route existe et répond 501. */
export interface CircuitExterne {
  libelle: string;
  libelleEn?: string;
  /** Ce que la route refuse de faire, en français clair. */
  motif: string;
  motifEn?: string;
  /** Appel de la route 501 : le message vient du serveur, pas de l'UI. */
  interroger: (id: number) => Promise<AxiosResponse>;
}

/** Clé d'une sonde : une seule entrée de la réponse serveur, affichée telle
 *  quelle. Aucun libellé ne correspond à un calcul fait côté navigateur. */
export interface CleSonde {
  /** Nom EXACT de la clé renvoyée par la route. */
  name: string;
  label: string;
  labelEn?: string;
  type?: 'montant' | 'nombre' | 'booleen' | 'date' | 'texte';
  unite?: string;
}

/** Lecture complémentaire en une ligne : la route existe et renvoie des
 *  données agrégées par le serveur (écarts, totaux). Une valeur non calculable
 *  y est NULL : l'écran l'affiche « non enregistré » au lieu de combler. */
export interface SondeServeur {
  id: string;
  libelle: string;
  libelleEn?: string;
  /** Permission granulaire requise (défaut : lecture). */
  action?: 'read' | 'modify' | 'approve';
  interroger: (id: number) => Promise<AxiosResponse>;
  cles: CleSonde[];
  /** Rappel du périmètre exact de la route, en langage d'agent. */
  note?: string;
  noteEn?: string;
}

export interface ConfigRegistre {
  /** Sous-module dans le catalogue de permissions backend. */
  permSousModule: string;
  tcode: string;
  icon: LucideIcon;
  titre: string;
  titreEn: string;
  description: string;
  descriptionEn: string;
  /** Aide contextuelle (processus réel, pas une astuce cosmétique). */
  aide: string;
  aideEn: string;
  lister: (params: Record<string, string | number | boolean>) => Promise<AxiosResponse>;
  creer: (data: ChargementRegistre) => Promise<AxiosResponse>;
  modifier: (id: number, data: ChargementRegistre) => Promise<AxiosResponse>;
  /** Aucune suppression « sèche » n'est exposée : les deux seules routes DELETE
   *  du département (projets, infrastructures) exigent un MOTIF écrit, donc
   *  passent par `actions` avec `action: 'delete'`. Une pièce à valeur
   *  documentaire n'est quant à elle jamais effacée : elle est abrogée,
   *  annulée ou résiliée — d'où l'absence de retrait sur la plupart. */
  colonnes: ColonneRegistre[];
  champs: ChampRegistre[];
  filtres?: FiltreRegistre[];
  actions?: ActionRegistre[];
  /** Agrégats relus à la demande sur une ligne (routes GET dédiées). */
  sondes?: SondeServeur[];
  circuits?: CircuitExterne[];
  /** Une seule ligne = une seule référence : le serveur renvoie 409. */
  unicite?: string;
}

/** Réponse de /nomenclatures : { cle: [{ code, valeur }] }. */
export type Nomenclatures = Record<string, { code: string; valeur: string }[]>;

/** Éléments de /places (référentiel national ports_cameroun).
 *
 *  Copie conforme de ce que la route sert : un champ NOT NULL en base n'est pas
 *  nullable ici, mais tout le reste peut être null — « non enregistré » veut
 *  dire que l'agent n'a pas encore recopié le document officiel, pas que la
 *  valeur est nulle. La déclaration d'une place (code, nom, type_port) se fait
 *  depuis le centre de pilotage, jamais par un seed applicatif. */
export interface PlacePortuaire {
  id: number;
  code: string;
  nom: string | null;
  type_port: string | null;
  ville: string | null;
  region: string | null;
  autorite_portuaire: string | null;
  operateur: string | null;
  tirant_eau_max: number | null;
  profondeur_m: number | null;
  capacite_annuelle_tonnes: number | null;
  nombre_postes_quai: number | null;
  zone_franche: boolean | null;
  date_ouverture: string | null;
  /** Seule colonne du référentiel où l'agent peut citer son document officiel :
   *  ports_cameroun ne porte ni source_reference ni notes. */
  localisation: string | null;
  description: string | null;
  /** false = place sortie du périmètre (jamais supprimée : référentiel partagé). */
  est_actif: boolean;
}
