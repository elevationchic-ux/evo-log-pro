'use client';

/**
 * RegistrePortuaire — châssis commun des neuf registres du département
 * Aménagement portuaire & Domaine public.
 *
 * Pourquoi un châssis et pas neuf pages dupliquées : les objets diffèrent par
 * leurs champs, pas par leur usage (consulter, saisir, instrumentaliser un
 * acte). La configuration declarative (registres.ts) porte donc le vocabulaire
 * métier, et ce composant porte uniquement la mécanique honnête :
 *
 *  1. les options des listes déroulantes viennent de `/nomenclatures` et les
 *     places de `/places` : aucun choix n'est figé dans le composant ;
 *  2. un champ laissé vide n'est PAS envoyé : le backend (`exclude_unset`)
 *     laisse NULL, et l'écran affiche « non enregistré » ;
 *  3. écrire est conditionné par la permission granulaire réelle
 *     (`amenagement.<sous-module>.<action>`), la même que vérifie l'API ;
 *  4. les téléprocédures institutionnelles (MINMIVT, COLIFE, MINFI…) sont
 *     annoncées, jamais simulées : la route répond 501 et le message du
 *     serveur est affiché tel quel ;
 *  5. erreur serveur = son `detail` (409 sur une référence déjà enregistrée
 *     par exemple), pas un texte générique qui masquerait le doublon.
 */
import React, { useCallback, useMemo, useState } from 'react';
import { Pencil, Plus, RefreshCw, ShieldAlert, WifiOff, Trash2, FileQuestion, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';
import type { AxiosError } from 'axios';

import ModuleLayout from '@/components/layout/ModuleLayout';
import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { useApi, classifyApiError } from '@/hooks/useApi';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';
import { amenagementAPI } from '@/lib/api-client';

import type {
  ActionRegistre,
  ChampRegistre,
  ChargementRegistre,
  ConfigRegistre,
  LigneRegistre,
  Nomenclatures,
  PlacePortuaire,
} from './typesRegistre';
import {
  aideChamp,
  estAbsent,
  labelChamp,
  labelColonne,
  rendreCellule,
  saisieVide,
  tManquant,
  valeurSaisie,
} from './formatRegistre';

/* --------------------------- utilitaires locaux --------------------------- */

/** Le backend FastAPI renvoie ses refus métier dans `detail` (string) ; les
 *  erreurs de validation Pydantic en liste (422). On affiche le texte du
 *  serveur, et seulement lui — jamais un message générique qui effacerait la
 *  raison réelle (doublon de référence, dépendance absente…). */
function messageServeur(err: unknown, fallback: string): string {
  const ax = err as AxiosError;
  const detail = (ax?.response?.data as { detail?: unknown } | undefined)?.detail;
  if (typeof detail === 'string' && detail.trim()) return detail.trim();
  if (Array.isArray(detail) && detail.length) {
    const premier = detail[0] as { msg?: string; loc?: (string | number)[] };
    const champ = premier?.loc?.[premier.loc.length - 1];
    return `${champ ? `${champ} : ` : ''}${premier?.msg || 'donnée refusée par le serveur'}`;
  }
  const info = classifyApiError(err);
  return info.message || fallback;
}

type Tri = '' | 'oui' | 'non';

/** Booléen en trois états. Un case à cocher classique imposerait « Non » à
 *  chaque création : ici « laisser vide » reste une information absente (NULL
 *  en base), conformément au schéma Pydantic qui déclare le champ Optionnel. */
function champTriplet(v: unknown): Tri {
  if (v === true) return 'oui';
  if (v === false) return 'non';
  return '';
}

/* ------------------------------ formulaire ------------------------------- */

function ChampSaisie({
  champ,
  valeur,
  onChange,
  nomenclatures,
  places,
  lang,
  lectureSeule,
}: {
  champ: ChampRegistre;
  valeur: string;
  onChange: (v: string) => void;
  nomenclatures: Nomenclatures | null;
  places: PlacePortuaire[];
  lang: 'fr' | 'en';
  lectureSeule: boolean;
}) {
  const aide = aideChamp(champ, lang);
  const classeChamp =
    'w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-600/60 disabled:opacity-50';

  const entrees = champ.nomenclature && nomenclatures ? nomenclatures[champ.nomenclature] || [] : [];

  return (
    <label className={`block ${champ.large ? 'sm:col-span-2' : ''}`}>
      <span className="block text-xs font-semibold text-slate-300 mb-1.5">
        {labelChamp(champ, lang)}
        {champ.requisCreation && <span className="text-amber-400"> *</span>}
      </span>

      {champ.type === 'zone' ? (
        <textarea
          rows={3}
          value={valeur}
          disabled={lectureSeule}
          onChange={(e) => onChange(e.target.value)}
          className={classeChamp}
          placeholder={aide || ''}
        />
      ) : champ.type === 'liste' ? (
        <textarea
          rows={3}
          value={valeur}
          disabled={lectureSeule}
          onChange={(e) => onChange(e.target.value)}
          className={`${classeChamp} font-mono text-xs`}
          placeholder={lang === 'en' ? 'One item per line' : 'Une valeur par ligne'}
        />
      ) : champ.type === 'select' && champ.depuisPlaces ? (
        <select
          value={valeur}
          disabled={lectureSeule}
          onChange={(e) => onChange(e.target.value)}
          className={classeChamp}
        >
          <option value="">{lang === 'en' ? 'Not recorded' : 'Non enregistré'}</option>
          {places.map((p) => (
            <option key={p.id} value={String(p.id)}>
              {p.nom || p.code}
              {p.code ? ` (${p.code})` : ''}
            </option>
          ))}
          {places.length === 0 && (
            <option value="" disabled>
              {lang === 'en' ? 'No port place in the national registry' : 'Aucune place dans le référentiel national'}
            </option>
          )}
        </select>
      ) : champ.type === 'select' ? (
        <select
          value={valeur}
          disabled={lectureSeule}
          onChange={(e) => onChange(e.target.value)}
          className={classeChamp}
        >
          <option value="">{lang === 'en' ? 'Not recorded' : 'Non enregistré'}</option>
          {entrees.map((e) => (
            <option key={e.code} value={e.valeur}>
              {e.valeur.replace(/[_-]+/g, ' ')}
            </option>
          ))}
          {entrees.length === 0 && (
            <option value="" disabled>
              {lang === 'en' ? 'Nomenclature unavailable' : 'Nomenclature indisponible'}
            </option>
          )}
        </select>
      ) : champ.type === 'booleen' ? (
        <select
          value={valeur}
          disabled={lectureSeule}
          onChange={(e) => onChange(e.target.value)}
          className={classeChamp}
        >
          <option value="">{tManquant(lang)}</option>
          <option value="oui">{lang === 'en' ? 'Yes' : 'Oui'}</option>
          <option value="non">{lang === 'en' ? 'No' : 'Non'}</option>
        </select>
      ) : (
        <input
          type={champ.type === 'date' ? 'date' : champ.type === 'nombre' || champ.type === 'montant' ? 'number' : 'text'}
          value={valeur}
          disabled={lectureSeule}
          min={champ.min}
          max={champ.max}
          step={champ.pas ?? (champ.type === 'montant' ? 1 : champ.type === 'nombre' ? '0.01' : undefined)}
          onChange={(e) => onChange(e.target.value)}
          className={classeChamp}
          placeholder={champ.type === 'montant' ? (lang === 'en' ? 'Amount in FCFA' : 'Montant en FCFA') : ''}
        />
      )}

      {aide && <span className="mt-1 block text-[11px] leading-relaxed text-slate-400">{aide}</span>}
      {champ.depuisPlaces && places.length === 0 && (
        <span className="mt-1 block text-[11px] text-amber-300/80">
          {lang === 'en'
            ? 'Port places come from the national registry: nothing is proposed until they are recorded there.'
            : 'Les places viennent du référentiel national : rien n\u2019est proposé tant qu\u2019elles n\u2019y sont pas enregistrées.'}
        </span>
      )}
    </label>
  );
}

/* ----------------------------- composant principal ---------------------------- */

type ModeFormulaire = 'ferme' | 'creation' | 'edition';

export default function RegistrePortuaire({ config }: { config: ConfigRegistre }) {
  const { language } = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const can = useCan();

  const perm = useCallback(
    (action: string) => `amenagement.${config.permSousModule}.${action}`,
    [config.permSousModule],
  );
  const peutLire = can(perm('read'));
  const peutCreer = can(perm('create'));
  const peutModifier = can(perm('modify'));
  const peutApprouver = can(perm('approve'));
  const peutSupprimer = can(perm('delete'));

  /* Référentiels servis par le serveur (aucune liste figée ici). */
  const nomenclatures = useApi<Nomenclatures | null>(
    async () => (await amenagementAPI.getNomenclatures()).data as Nomenclatures,
  );
  const places = useApi<PlacePortuaire[]>(
    async () => {
      const brut = (await amenagementAPI.getPlaces()).data as { data?: PlacePortuaire[] };
      return Array.isArray(brut?.data) ? brut.data : [];
    },
  );

  /* Filtres : l'état n'est pas un objet figé, chaque registre déclare ses
     propres paramètres de query côté serveur. */
  const [filtres, setFiltres] = useState<Record<string, string>>({});
  const filtresCourants = filtres;

  const lignes = useApi<LigneRegistre[]>(async () => {
    const params: Record<string, string | number | boolean> = {};
    Object.entries(filtresCourants).forEach(([cle, val]) => {
      if (saisieVide(val)) return;
      if (val === 'oui') params[cle] = true;
      else if (val === 'non') params[cle] = false;
      else params[cle] = val;
    });
    const brut = (await config.lister(params)).data;
    return Array.isArray(brut) ? (brut as LigneRegistre[]) : [];
  });

  const [mode, setMode] = useState<ModeFormulaire>('ferme');
  const [ligneEnCours, setLigneEnCours] = useState<LigneRegistre | null>(null);
  const [saisie, setSaisie] = useState<Record<string, string>>({});
  const [enCours, setEnCours] = useState(false);

  const [actionOuverte, setActionOuverte] = useState<ActionRegistre | null>(null);
  const [ligneAction, setLigneAction] = useState<LigneRegistre | null>(null);
  const [saisieAction, setSaisieAction] = useState<Record<string, string>>({});

  const [circuitOuvert, setCircuitOuvert] = useState<string | null>(null);
  const [reponseCircuit, setReponseCircuit] = useState<string | null>(null);
  const [sondeCircuit, setSondeCircuit] = useState(false);

  const ouvrirCreation = () => {
    const init: Record<string, string> = {};
    config.champs.forEach((c) => {
      init[c.name] = '';
    });
    setSaisie(init);
    setLigneEnCours(null);
    setMode('creation');
  };

  const ouvrirEdition = (ligne: LigneRegistre) => {
    const init: Record<string, string> = {};
    config.champs.forEach((c) => {
      const v = ligne[c.name];
      init[c.name] = c.type === 'booleen' ? champTriplet(v) : valeurSaisie(v);
    });
    setSaisie(init);
    setLigneEnCours(ligne);
    setMode('edition');
  };

  /** Construit le payload : un champ vide est ABSENT de l'envoi, pas vide.
   *  C'est ce qui garantit qu'un montant non saisi reste NULL en base. */
  const construirePayload = (champs: ChampRegistre[], source: Record<string, string>): ChargementRegistre => {
    const payload: ChargementRegistre = {};
    champs.forEach((c) => {
      const brut = source[c.name] ?? '';
      if (saisieVide(brut)) return;
      if (c.type === 'nombre' || c.type === 'montant') {
        const n = Number(brut);
        if (Number.isFinite(n)) payload[c.name] = n;
        return;
      }
      if (c.type === 'booleen') {
        if (brut === 'oui') payload[c.name] = true;
        else if (brut === 'non') payload[c.name] = false;
        return;
      }
      if (c.type === 'liste') {
        const morceaux = brut.split('\n').map((s) => s.trim()).filter(Boolean);
        if (morceaux.length) payload[c.name] = morceaux;
        return;
      }
      payload[c.name] = brut.trim();
    });
    return payload;
  };

  const manquantsRequis = useMemo(() => {
    if (mode !== 'creation') return [];
    return config.champs
      .filter((c) => c.requisCreation && saisieVide(saisie[c.name] ?? ''))
      .map((c) => labelChamp(c, lang));
  }, [mode, saisie, config.champs, lang]);

  const enregistrer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (manquantsRequis.length) {
      toast.error(t(
        `Champ obligatoire non renseigné : ${manquantsRequis.join(', ')}`,
        `Required field missing: ${manquantsRequis.join(', ')}`,
      ));
      return;
    }
    setEnCours(true);
    try {
      const payload = construirePayload(config.champs, saisie);
      if (mode === 'edition' && ligneEnCours) {
        await config.modifier(ligneEnCours.id, payload);
        toast.success(t('Ligne du registre corrigée.', 'Register line updated.'));
      } else {
        await config.creer(payload);
        toast.success(t('Pièce enregistrée dans le registre.', 'Document recorded in the register.'));
      }
      setMode('ferme');
      lignes.refetch();
    } catch (err) {
      toast.error(messageServeur(err, t('Enregistrement impossible.', 'Could not save.')));
    } finally {
      setEnCours(false);
    }
  };

  const supprimer = async (ligne: LigneRegistre) => {
    if (!config.supprimer) return;
    const lib = String(ligne[config.colonnes[0]?.name] ?? ligne.id);
    if (!window.confirm(t(
      `Retirer du registre la ligne « ${lib} » ? Cette action est irréversible et ne vaut pas abrogation de l'acte : enregistrez plutôt son annulation si la pièce a produit des effets.`,
      `Remove line “${lib}” from the register? This is irreversible and does not repeal the act: record its cancellation instead if the document took effect.`,
    ))) return;
    setEnCours(true);
    try {
      await config.supprimer(ligne.id);
      toast.success(t('Ligne retirée du registre.', 'Line removed from the register.'));
      lignes.refetch();
    } catch (err) {
      toast.error(messageServeur(err, t('Suppression impossible.', 'Could not delete.')));
    } finally {
      setEnCours(false);
    }
  };

  const ouvrirAction = (action: ActionRegistre, ligne: LigneRegistre) => {
    const init: Record<string, string> = {};
    action.champs.forEach((c) => {
      const v = ligne[c.name];
      init[c.name] = c.type === 'booleen' ? champTriplet(v) : valeurSaisie(v);
    });
    setSaisieAction(init);
    setLigneAction(ligne);
    setActionOuverte(action);
  };

  const lancerAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionOuverte || !ligneAction) return;
    const requisManquants = actionOuverte.champs
      .filter((c) => c.requisCreation && saisieVide(saisieAction[c.name] ?? ''))
      .map((c) => labelChamp(c, lang));
    if (requisManquants.length) {
      toast.error(t(`Champ obligatoire non renseigné : ${requisManquants.join(', ')}`, `Required field missing: ${requisManquants.join(', ')}`));
      return;
    }
    setEnCours(true);
    try {
      await actionOuverte.executer(ligneAction.id, construirePayload(actionOuverte.champs, saisieAction));
      toast.success(actionOuverte.succesEn && lang === 'en' ? actionOuverte.succesEn : actionOuverte.succes);
      setActionOuverte(null);
      lignes.refetch();
    } catch (err) {
      toast.error(messageServeur(err, t('Opération refusée par le serveur.', 'Operation refused by the server.')));
    } finally {
      setEnCours(false);
    }
  };

  /** Sonde une téléprocédure non câblée : le 501 et son motif viennent du
   *  serveur, on n'écrit pas ici ce que le backend refuse de promettre. */
  const sonderCircuit = async (index: string, ident: number, interroger: (id: number) => Promise<unknown>) => {
    setSondeCircuit(true);
    setReponseCircuit(null);
    try {
      await interroger(ident);
      setReponseCircuit(t(
        'Le serveur a répondu sans erreur : cette écriture est en réalité disponible, l\u2019écran doit être mis à jour.',
        'The server answered without error: this write is actually available and the screen should be updated.',
      ));
    } catch (err) {
      setReponseCircuit(messageServeur(err, t('Réseau indisponible.', 'Network unavailable.')));
    } finally {
      setSondeCircuit(false);
      setCircuitOuvert(index);
    }
  };

  /* ------------------------------- colonnes ------------------------------- */
  const colonnesEssentielles = config.colonnes.filter((c) => c.essence);
  const colonnesTable = config.colonnes;

  const renduLigne = (ligne: LigneRegistre) => {
    const actionsLigne: React.ReactNode[] = [];
    if (peutModifier) {
      actionsLigne.push(
        <button
          key="edit"
          type="button"
          onClick={() => ouvrirEdition(ligne)}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-[11px] font-semibold text-slate-200 hover:bg-slate-700"
          title={t('Corriger la saisie', 'Edit the entry')}
        >
          <Pencil className="w-3.5 h-3.5" />
          {t('Corriger', 'Edit')}
        </button>,
      );
    }
    (config.actions || [])
      .filter((a) => can(perm(a.action)))
      .forEach((a) => {
        actionsLigne.push(
          <button
            key={a.id}
            type="button"
            onClick={() => ouvrirAction(a, ligne)}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-cyan-900/40 border border-cyan-700/50 text-[11px] font-semibold text-cyan-200 hover:bg-cyan-800/50"
            title={a.avertissement || t('Enregistrer cet acte', 'Record this act')}
          >
            <FileQuestion className="w-3.5 h-3.5" />
            {a.libelleEn && lang === 'en' ? a.libelleEn : a.libelle}
          </button>,
        );
      });
    if (peutSupprimer && config.supprimer) {
      actionsLigne.push(
        <button
          key="del"
          type="button"
          onClick={() => supprimer(ligne)}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-red-900/30 border border-red-800/50 text-[11px] font-semibold text-red-200 hover:bg-red-900/50"
          title={t('Retirer la ligne', 'Remove the line')}
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>,
      );
    }
    return actionsLigne;
  };

  /* -------------------------------- rendu -------------------------------- */
  const entete = (
    <div className="flex flex-wrap items-center gap-2">
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 font-mono text-[11px] text-cyan-300">
        {config.tcode}
      </span>
      {peutCreer && (
        <button
          type="button"
          onClick={ouvrirCreation}
          className="inline-flex items-center gap-1.5 px-4 py-2 min-h-11 rounded-xl bg-cyan-600 text-slate-950 text-xs font-bold hover:bg-cyan-500 transition-colors"
        >
          <Plus className="w-4 h-4" />
          {t('Enregistrer une pièce', 'Record a document')}
        </button>
      )}
      <button
        type="button"
        onClick={() => { lignes.refetch(); nomenclatures.refetch(); places.refetch(); }}
        className="inline-flex items-center gap-1.5 px-3 py-2 min-h-11 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-700"
        title={t('Recharger le registre et les référentiels', 'Reload the register and the references')}
      >
        <RefreshCw className="w-4 h-4" />
        {t('Recharger', 'Reload')}
      </button>
    </div>
  );

  return (
    <ModuleLayout
      title={lang === 'en' ? config.titreEn : config.titre}
      description={lang === 'en' ? config.descriptionEn : config.description}
      help={lang === 'en' ? config.aideEn : config.aide}
      actions={entete}
    >
      {/* Le module n'est pas acquis au rôle : on le dit, sans afficher un
          tableau vide qui laisserait croire à une base réellement vide. */}
      {!peutLire ? (
        <div className="flex items-start gap-3 rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-sm text-slate-300 leading-relaxed">
            {t(
              `Votre rôle ne dispose pas de la permission ${perm('read')}. Le registre existe côté serveur, mais sa consultation ne vous est pas ouverte : demandez cet habilitament à l'administrateur de votre tenant.`,
              `Your role does not hold the ${perm('read')} permission. The register exists on the server but is not open to you: request this accreditation from your tenant administrator.`,
            )}
          </p>
        </div>
      ) : (
        <>
          {/* Filtres déclarés par le registre (paramètres de query réels). */}
          {config.filtres && config.filtres.length > 0 && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {config.filtres.map((f) => {
                  const entrees = f.nomenclature && nomenclatures.data ? nomenclatures.data[f.nomenclature] || [] : [];
                  return (
                    <label key={f.name} className="block">
                      <span className="block text-[11px] font-semibold text-slate-400 mb-1">
                        {f.labelEn && lang === 'en' ? f.labelEn : f.label}
                      </span>
                      {f.type === 'select' || f.booleen ? (
                        <select
                          value={filtres[f.name] ?? ''}
                          onChange={(e) => setFiltres((prev) => ({ ...prev, [f.name]: e.target.value }))}
                          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-600/60"
                        >
                          <option value="">{t('Tous', 'All')}</option>
                          {f.booleen ? (
                            <>
                              <option value="oui">{t('Oui', 'Yes')}</option>
                              <option value="non">{t('Non', 'No')}</option>
                            </>
                          ) : f.depuisPlaces ? (
                            places.data?.map((p) => (
                              <option key={p.id} value={String(p.id)}>{p.nom || p.code}</option>
                            ))
                          ) : (
                            entrees.map((e) => (
                              <option key={e.code} value={e.valeur}>{e.valeur.replace(/[_-]+/g, ' ')}</option>
                            ))
                          )}
                        </select>
                      ) : (
                        <input
                          type={f.type === 'date' ? 'date' : f.type === 'nombre' ? 'number' : 'text'}
                          value={filtres[f.name] ?? ''}
                          onChange={(e) => setFiltres((prev) => ({ ...prev, [f.name]: e.target.value }))}
                          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-xs text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-600/60"
                        />
                      )}
                    </label>
                  );
                })}
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => lignes.refetch()}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-700/70 text-slate-950 text-[11px] font-bold hover:bg-cyan-600"
                >
                  {t('Filtrer', 'Filter')}
                </button>
                <button
                  type="button"
                  onClick={() => { setFiltres({}); setTimeout(() => lignes.refetch(), 0); }}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-[11px] font-semibold text-slate-300 hover:bg-slate-700"
                >
                  {t('Tout afficher', 'Show all')}
                </button>
                <span className="text-[11px] text-slate-500">
                  {t(
                    'Le filtrage est exécuté par le serveur, sur les colonnes du registre.',
                    'Filtering runs server-side, on the register columns.',
                  )}
                </span>
              </div>
            </div>
          )}

          {/* Avertissement de référentiel : une nomenclature indisponible est
              annoncée, pas masquée (les listes vident plutôt que d'inventer). */}
          {nomenclatures.error && (
            <div className="flex items-start gap-2 rounded-xl border border-amber-600/40 bg-amber-600/10 px-3 py-2 text-[11px] text-amber-200">
              <WifiOff className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              <span>
                {t(
                  'Les vocabulaires du département ne sont pas chargés : les listes déroulantes restent vides au lieu de proposer des choix inventés.',
                  'Department vocabularies are not loaded: dropdowns stay empty instead of offering invented choices.',
                )}
              </span>
            </div>
          )}

          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 sm:p-5 backdrop-blur-xl">
            {lignes.loading ? (
              <DataLoadingState rows={5} label={t('Chargement du registre…', 'Loading the register…')} />
            ) : lignes.error ? (
              <DataErrorState error={lignes.error} onRetry={lignes.refetch} />
            ) : lignes.isEmpty ? (
              <DataEmptyState
                title={t('Aucune pièce enregistrée', 'No document recorded')}
                description={t(
                  'Le registre est vide : ce n\u2019est pas une panne. Rien n\u2019est affiché tant qu\u2019aucun acte n\u2019a été saisi depuis un document réel (arrêté, DAO, contrat, relevé).',
                  'The register is empty: this is not a failure. Nothing is shown until an act has been entered from a real document (order, tender, contract, survey).',
                )}
                actionLabel={peutCreer ? t('Enregistrer la première pièce', 'Record the first document') : undefined}
                onAction={peutCreer ? ouvrirCreation : undefined}
              />
            ) : (
              <>
                {/* Tableau desktop */}
                <div className="hidden lg:block overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left border-b border-slate-800">
                        {colonnesTable.map((c) => (
                          <th key={c.name} className="py-2.5 pr-4 text-[11px] font-bold uppercase tracking-wide text-slate-400">
                            {labelColonne(c, lang)}
                          </th>
                        ))}
                        <th className="py-2.5 text-[11px] font-bold uppercase tracking-wide text-slate-400">
                          {t('Actes', 'Acts')}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {(lignes.data || []).map((ligne) => (
                        <tr key={ligne.id} className="border-b border-slate-800/60 hover:bg-slate-800/30">
                          {colonnesTable.map((c) => {
                            const cell = rendreCellule(c, ligne, lang, nomenclatures.data || null);
                            return (
                              <td
                                key={c.name}
                                className={`py-2.5 pr-4 max-w-[22rem] align-top ${cell.manquant ? 'text-slate-500 italic' : 'text-slate-100'} ${c.type === 'code' ? 'font-mono text-xs' : ''}`}
                              >
                                {cell.texte}
                              </td>
                            );
                          })}
                          <td className="py-2.5">
                            <div className="flex flex-wrap gap-1.5">{renduLigne(ligne)}</div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Cartes mobile : uniquement les colonnes essentielles. */}
                <div className="space-y-3 lg:hidden">
                  {(lignes.data || []).map((ligne) => (
                    <article key={ligne.id} className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                      <div className="space-y-1.5">
                        {colonnesEssentielles.map((c) => {
                          const cell = rendreCellule(c, ligne, lang, nomenclatures.data || null);
                          return (
                            <div key={c.name} className="flex items-baseline justify-between gap-3">
                              <span className="text-[11px] uppercase tracking-wide text-slate-500">
                                {labelColonne(c, lang)}
                              </span>
                              <span className={`text-sm text-right ${cell.manquant ? 'text-slate-500 italic' : 'text-slate-100 font-semibold'}`}>
                                {cell.texte}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                      <div className="mt-3 flex flex-wrap gap-1.5">{renduLigne(ligne)}</div>
                    </article>
                  ))}
                </div>

                <p className="mt-4 text-[11px] text-slate-500 leading-relaxed">
                  {t(
                    `${(lignes.data || []).length} ligne(s) affichée(s). Un libellé en gris italique signifie « non enregistré » : la donnée n'existe pas encore, elle n'a pas été estimée.`,
                    `${(lignes.data || []).length} row(s) shown. A grey italic value means “not recorded”: the data does not exist yet and was not estimated.`,
                  )}
                </p>
              </>
            )}
          </div>

          {/* Circuits institutionnels : routes 501, annoncées et sondables. */}
          {config.circuits && config.circuits.length > 0 && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 sm:p-5">
              <h2 className="text-sm font-bold text-slate-200">
                {t('Circuit institutionnel non câblé', 'Institutional pipeline not connected')}
              </h2>
              <p className="mt-1 text-xs text-slate-400 leading-relaxed">
                {t(
                  'Ces échanges appartiennent à des systèmes externes qui n\u2019existent pas dans ce logiciel. Le backend refuse de les simuler et répond 501 : vous pouvez lui demander le motif exact.',
                  'These exchanges belong to external systems that do not exist in this software. The backend refuses to simulate them and answers 501: you can ask it for the exact reason.',
                )}
              </p>
              <ul className="mt-3 space-y-2">
                {config.circuits.map((c, index) => {
                  const cle = `${config.permSousModule}-${index}`;
                  return (
                    <li key={cle} className="rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-slate-200">
                            {c.libelleEn && lang === 'en' ? c.libelleEn : c.libelle}
                          </p>
                          <p className="mt-1 text-[11px] text-slate-400 leading-relaxed">
                            {c.motifEn && lang === 'en' ? c.motifEn : c.motif}
                          </p>
                          {circuitOuvert === cle && reponseCircuit && (
                            <p className="mt-2 text-[11px] font-mono text-cyan-300/90 break-words">
                              serveur : {reponseCircuit}
                            </p>
                          )}
                        </div>
                        <button
                          type="button"
                          disabled={sondeCircuit}
                          onClick={() => sonderCircuit(cle, 0, c.interroger)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-[11px] font-semibold text-slate-300 hover:bg-slate-700 disabled:opacity-50"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          {t('Demander le motif au serveur', 'Ask the server for the reason')}
                        </button>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </>
      )}

      {/* Modale de saisie / correction */}
      {mode !== 'ferme' && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/70 p-4 overflow-y-auto">
          <form
            onSubmit={enregistrer}
            className="w-full max-w-3xl my-8 bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6"
          >
            <h2 className="text-lg font-bold text-slate-100">
              {mode === 'creation'
                ? t('Enregistrer une pièce', 'Record a document')
                : t('Corriger la saisie', 'Edit the entry')}
            </h2>
            <p className="mt-1 text-xs text-slate-400 leading-relaxed">
              {t(
                'Un champ laissé vide n\u2019est pas envoyé : il restera « non enregistré » au registre. Aucune valeur n\u2019est calculée à votre place.',
                'A field left blank is not sent: it stays “not recorded” in the register. No value is computed for you.',
              )}
            </p>
            {config.unicite && mode === 'creation' && (
              <p className="mt-2 text-[11px] text-amber-300/90">
                {t(
                  `La référence « ${config.unicite} » doit être l'unique ligne de ce document : le serveur refuse un doublon.`,
                  `The “${config.unicite}” reference must be unique: the server rejects duplicates.`,
                )}
              </p>
            )}

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
              {config.champs.map((c) => (
                <ChampSaisie
                  key={c.name}
                  champ={c}
                  valeur={saisie[c.name] ?? ''}
                  onChange={(v) => setSaisie((prev) => ({ ...prev, [c.name]: v }))}
                  nomenclatures={nomenclatures.data || null}
                  places={places.data || []}
                  lang={lang}
                  lectureSeule={mode === 'edition' && !!c.lectureSeuleEdition}
                />
              ))}
            </div>

            <div className="mt-6 flex flex-wrap justify-end gap-2">
              <button
                type="button"
                onClick={() => setMode('ferme')}
                className="px-4 py-2 min-h-11 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-700"
              >
                {t('Annuler', 'Cancel')}
              </button>
              <button
                type="submit"
                disabled={enCours}
                className="px-5 py-2 min-h-11 rounded-xl bg-cyan-600 text-slate-950 text-xs font-bold hover:bg-cyan-500 disabled:opacity-60"
              >
                {enCours ? t('Enregistrement…', 'Saving…') : t('Enregistrer', 'Save')}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Modale d'action (acte juridique ou financier consigné) */}
      {actionOuverte && ligneAction && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/70 p-4 overflow-y-auto">
          <form
            onSubmit={lancerAction}
            className="w-full max-w-xl my-8 bg-slate-900 border border-slate-800 rounded-2xl p-5 sm:p-6"
          >
            <h2 className="text-lg font-bold text-slate-100">
              {actionOuverte.libelleEn && lang === 'en' ? actionOuverte.libelleEn : actionOuverte.libelle}
            </h2>
            {actionOuverte.avertissement && (
              <p className="mt-2 rounded-xl border border-cyan-800/50 bg-cyan-950/40 px-3 py-2 text-[11px] leading-relaxed text-cyan-200">
                {actionOuverte.avertissementEn && lang === 'en' ? actionOuverte.avertissementEn : actionOuverte.avertissement}
              </p>
            )}
            <p className="mt-2 text-[11px] text-slate-400 font-mono">
              {t('Ligne concernée', 'Affected line')} : {String(ligneAction[config.colonnes[0]?.name] ?? ligneAction.id)}
            </p>

            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
              {actionOuverte.champs.map((c) => (
                <ChampSaisie
                  key={c.name}
                  champ={c}
                  valeur={saisieAction[c.name] ?? ''}
                  onChange={(v) => setSaisieAction((prev) => ({ ...prev, [c.name]: v }))}
                  nomenclatures={nomenclatures.data || null}
                  places={places.data || []}
                  lang={lang}
                  lectureSeule={false}
                />
              ))}
            </div>

            <div className="mt-6 flex flex-wrap justify-end gap-2">
              <button
                type="button"
                onClick={() => setActionOuverte(null)}
                className="px-4 py-2 min-h-11 rounded-xl bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-700"
              >
                {t('Annuler', 'Cancel')}
              </button>
              <button
                type="submit"
                disabled={enCours}
                className="px-5 py-2 min-h-11 rounded-xl bg-cyan-600 text-slate-950 text-xs font-bold hover:bg-cyan-500 disabled:opacity-60"
              >
                {enCours ? t('Consignation…', 'Recording…') : t('Consigner', 'Record')}
              </button>
            </div>
          </form>
        </div>
      )}
    </ModuleLayout>
  );
}

export { peutAfficherValeur } from './formatRegistre';
