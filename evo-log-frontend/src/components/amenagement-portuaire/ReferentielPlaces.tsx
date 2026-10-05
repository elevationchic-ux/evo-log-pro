'use client';

/**
 * ReferentielPlaces — écran de déclaration du référentiel national des places.
 *
 * Pourquoi ce panneau existe : les neuf registres du département rattachent
 * leurs lignes à une `port_id` lue dans `ports_cameroun`, et cette table
 * nationale n'était écrite par AUCUNE route de l'application — le département
 * ne pouvait donc jamais être démarré, et chaque formulaire restait vide.
 *
 * Ce que ce composant refuse de faire :
 *  - il n'écrit aucun nom de port, aucun code, aucune nature de port en dur :
 *    les valeurs admises de `type_port` viennent de `/nomenclatures` et la
 *    liste des places de `/places` ;
 *  - il n'enregistre pas une place « technique » sans le document officiel :
 *    le serveur exige `code`, `nom` et `type_port` (422 sinon) et le formulaire
 *    ne remplit rien à la place de l'agent ;
 *  - un champ laissé vide n'est pas envoyé : la colonne reste NULL et
 *    s'affiche « non enregistré » ;
 *  - aucune suppression : `ports_cameroun` est partagé (terminaux,
 *    tarification, périmètres). Sortir du périmètre = `est_actif` faux ;
 *  - les erreurs du serveur sont affichées telles quelles (409 doublon de
 *    code, 422 type manquant), jamais remplacées par un texte générique.
 */
import React, { useCallback, useMemo, useState } from 'react';
import { MapPin, Pencil, Plus, ShieldAlert, X } from 'lucide-react';
import { toast } from 'sonner';
import type { AxiosError } from 'axios';

import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { useApi, classifyApiError } from '@/hooks/useApi';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';
import { amenagementAPI } from '@/lib/api-client';

import type { Nomenclatures, PlacePortuaire } from './typesRegistre';
import { estAbsent, formaterDate, formaterMesure, humaniser, libelleEnum, saisieVide, tManquant, valeurSaisie } from './formatRegistre';

/** Message du serveur, tel quel (FastAPI rend ses refus dans `detail`). */
function messageServeur(err: unknown, fallback: string): string {
  const detail = (err as AxiosError)?.response?.data?.detail as unknown;
  if (typeof detail === 'string' && detail.trim()) return detail.trim();
  if (Array.isArray(detail) && detail.length) {
    const premier = detail[0] as { msg?: string; loc?: (string | number)[] };
    const champ = premier?.loc?.[premier.loc.length - 1];
    return `${champ ? `${champ} : ` : ''}${premier?.msg || 'donnée refusée par le serveur'}`;
  }
  return classifyApiError(err).message || fallback;
}

/** Champs du formulaire de place : la description de ce que la route accepte
 *  (PlacePortuaireCreate / PlacePortuaireUpdate). `requis` reproduit la
 *  contrainte Pydantic pour désactiver l'envoi, pas pour la remplacer. */
type ChampPlace = {
  name: string;
  label: string;
  labelEn: string;
  type: 'texte' | 'nombre' | 'date' | 'zone' | 'select' | 'booleen';
  requis?: boolean;
  nomenclature?: string;
  unite?: string;
  aide?: string;
  aideEn?: string;
  /** Immuable après déclaration : le code identifie la place nationale. */
  lectureSeuleEdition?: boolean;
};

const CHAMPS_PLACE: ChampPlace[] = [
  {
    name: 'code',
    label: 'Code national',
    labelEn: 'National code',
    type: 'texte',
    requis: true,
    lectureSeuleEdition: true,
    aide: 'Tel que porté au document officiel (DOU, KRI, LIM…). Le serveur refuse un code déjà enregistré.',
    aideEn: 'As stated on the official document (DOU, KRI, LIM…). The server rejects an already-registered code.',
  },
  { name: 'nom', label: 'Dénomination', labelEn: 'Name', type: 'texte', requis: true, aide: 'Nom exact du port, sans abréviation commode.', aideEn: 'Exact port name, no convenient abbreviation.' },
  { name: 'type_port', label: 'Nature du port', labelEn: 'Port type', type: 'select', nomenclature: 'type_port', requis: true, aide: 'Valeurs servies par /nomenclatures : rien n’est proposé que le serveur n’admette.', aideEn: 'Values served by /nomenclatures: nothing offered that the server does not admit.' },
  { name: 'autorite_portuaire', label: 'Autorité portuaire', labelEn: 'Port authority', type: 'texte', aide: 'L’autorité concessionnaire du domaine (loi 2012/021), distincte de l’exploitant.', aideEn: 'The domain-concession authority (law 2012/021), distinct from the operator.' },
  { name: 'operateur', label: 'Exploitant', labelEn: 'Operator', type: 'texte', aide: 'Société d’exploitation telle que nommée au contrat.', aideEn: 'Operating company as named in the contract.' },
  { name: 'ville', label: 'Ville', labelEn: 'City', type: 'texte' },
  { name: 'region', label: 'Région', labelEn: 'Region', type: 'texte' },
  { name: 'localisation', label: 'Repère géographique', labelEn: 'Geographic fix', type: 'texte' },
  { name: 'tirant_eau_max', label: 'Tirant d’eau max', labelEn: 'Max draft', type: 'nombre', unite: 'm', aide: 'Relevé sur arrêté d’exploitation ou bathymétrie visée.', aideEn: 'Taken from the operating order or endorsed bathymetry.' },
  { name: 'profondeur_m', label: 'Profondeur', labelEn: 'Depth', type: 'nombre', unite: 'm' },
  { name: 'capacite_annuelle_tonnes', label: 'Capacité annuelle', labelEn: 'Annual capacity', type: 'nombre', unite: 't', aide: 'Jamais déduite du trafic observé : valeur publiée.', aideEn: 'Never inferred from observed traffic: a published figure.' },
  { name: 'nombre_postes_quai', label: 'Postes à quai', labelEn: 'Berths', type: 'nombre' },
  { name: 'zone_franche', label: 'Zone franche', labelEn: 'Free zone', type: 'booleen' },
  { name: 'date_ouverture', label: 'Date d’ouverture', labelEn: 'Opening date', type: 'date' },
  { name: 'description', label: 'Document source & observation', labelEn: 'Source document & note', type: 'zone', aide: 'ports_cameroun ne porte pas de colonne de traçabilité : citez ici l’arrêté ou le bail dont vous recopérez ces valeurs.', aideEn: 'ports_cameroun carries no traceability column: cite here the order or lease you are copying these values from.' },
];

/** Colonnes du tableau : chaque en-tête est un label d'interface, chaque valeur
 *  vient de la ligne serveurs. `type` pilote uniquement le formatage. */
const COLONNES_PLACE: { name: keyof PlacePortuaire; label: string; labelEn: string; type?: 'date' | 'nombre' | 'booleen' | 'enum'; unite?: string }[] = [
  { name: 'nom', label: 'Dénomination', labelEn: 'Name' },
  { name: 'type_port', label: 'Nature', labelEn: 'Type', type: 'enum' },
  { name: 'autorite_portuaire', label: 'Autorité portuaire', labelEn: 'Port authority' },
  { name: 'operateur', label: 'Exploitant', labelEn: 'Operator' },
  { name: 'tirant_eau_max', label: 'Tirant d’eau', labelEn: 'Draft', type: 'nombre', unite: 'm' },
  { name: 'capacite_annuelle_tonnes', label: 'Capacité', labelEn: 'Capacity', type: 'nombre', unite: 't' },
  { name: 'date_ouverture', label: 'Ouverture', labelEn: 'Opening', type: 'date' },
];

type Tri = '' | 'oui' | 'non';

function champTriplet(v: unknown): Tri {
  if (v === true) return 'oui';
  if (v === false) return 'non';
  return '';
}

/** Formate une colonne du référentiel. Une place n'est pas une ligne de
 *  registre (pas de ColonneRegistre côté schéma) : le formatage est donc dit
 *  ici, champ par champ, avec les mêmes règles d'absence que le châssis. */
function cellulePlace(
  colonne: (typeof COLONNES_PLACE)[number],
  ligne: PlacePortuaire,
  lang: 'fr' | 'en',
  nomenclatures: Nomenclatures | null,
): { texte: string; manquant: boolean } {
  const v = ligne[colonne.name];
  switch (colonne.type) {
    case 'date':
      return estAbsent(v)
        ? { texte: tManquant(lang), manquant: true }
        : { texte: formaterDate(String(v), lang), manquant: false };
    case 'nombre':
      return colonne.unite
        ? { texte: formaterMesure(typeof v === 'number' ? v : null, colonne.unite, lang), manquant: estAbsent(v) }
        : estAbsent(v)
          ? { texte: tManquant(lang), manquant: true }
          : { texte: String(v), manquant: false };
    case 'booleen':
      if (v === true) return { texte: lang === 'en' ? 'Yes' : 'Oui', manquant: false };
      if (v === false) return { texte: lang === 'en' ? 'No' : 'Non', manquant: false };
      return { texte: tManquant(lang), manquant: true };
    case 'enum': {
      // `type_port` est traduit par la nomenclature serveur, jamais par une
      // table de libellés recopiée dans le composant.
      const lib = libelleEnum(typeof v === 'string' ? v : null, 'type_port', nomenclatures);
      return lib === null ? { texte: tManquant(lang), manquant: true } : { texte: lib, manquant: false };
    }
    default:
      return estAbsent(v)
        ? { texte: tManquant(lang), manquant: true }
        : { texte: String(v), manquant: false };
  }
}

export default function ReferentielPlaces() {
  const { language } = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const can = useCan();

  const peutLire = can('amenagement.place.read');
  const peutDeclarer = can('amenagement.place.create');
  const peutCorriger = can('amenagement.place.modify');

  const [ouvert, setOuvert] = useState(false);
  const [edition, setEdition] = useState<PlacePortuaire | null>(null);
  const [saisie, setSaisie] = useState<Record<string, string>>({});
  const [enCours, setEnCours] = useState(false);

  /** Vocabulaire `type_port` servi par le serveur (jamais une liste figée ici). */
  const nomenclatures = useApi<Nomenclatures | null>(
    async () => (await amenagementAPI.getNomenclatures()).data as Nomenclatures,
    { isEmpty: (d) => !d || Object.keys(d).length === 0 },
  );

  const places = useApi<PlacePortuaire[]>(async () => {
    const brut = (await amenagementAPI.getPlaces()).data as { data?: PlacePortuaire[] };
    return Array.isArray(brut?.data) ? brut.data : [];
  });

  const rafraichir = useCallback(() => places.refetch(), [places]);

  const ouvrir = useCallback((ligne: PlacePortuaire | null) => {
    const init: Record<string, string> = {};
    CHAMPS_PLACE.forEach((c) => {
      const v = ligne ? (ligne[c.name] as string | number | boolean | null) : null;
      init[c.name] = c.type === 'booleen' ? champTriplet(v) : valeurSaisie(v);
    });
    setSaisie(init);
    setEdition(ligne);
    setOuvert(true);
  }, []);

  /** Payload : un champ vide est ABSENT de l'envoi (le backend `exclude_unset`
   *  laisse alors la colonne à NULL — c'est ce qui évite le zéro inventé). */
  const construire = useCallback((): Record<string, string | number | boolean> => {
    const payload: Record<string, string | number | boolean> = {};
    CHAMPS_PLACE.forEach((c) => {
      if (c.lectureSeuleEdition && edition) return;
      const brut = saisie[c.name] ?? '';
      if (saisieVide(brut)) return;
      if (c.type === 'nombre') {
        const n = Number(brut);
        if (Number.isFinite(n)) payload[c.name] = n;
        return;
      }
      if (c.type === 'booleen') {
        if (brut === 'oui') payload[c.name] = true;
        else if (brut === 'non') payload[c.name] = false;
        return;
      }
      payload[c.name] = c.type === 'texte' || c.type === 'zone' ? brut.trim() : brut;
    });
    return payload;
  }, [saisie, edition]);

  const requisManquants = useMemo(
    () =>
      CHAMPS_PLACE.filter((c) => c.requis)
        .filter((c) => {
          if (c.lectureSeuleEdition && edition) return false;
          return saisieVide(saisie[c.name] ?? '');
        })
        .map((c) => (lang === 'en' ? c.labelEn : c.label)),
    [saisie, edition, lang],
  );

  const enregistrer = async () => {
    if (!peutDeclarer && !peutCorriger) return;
    if (requisManquants.length) {
      toast.error(
        t(`Champs exigés par le serveur : ${requisManquants.join(', ')}.`, `Fields required by the server: ${requisManquants.join(', ')}.`),
      );
      return;
    }
    const payload = construire();
    if (!edition && saisieVide(payload.code as string | undefined)) return;
    setEnCours(true);
    try {
      if (edition) {
        await amenagementAPI.updatePlace(edition.id, payload);
        toast.success(t('Place corrigée dans le référentiel national.', 'Place corrected in the national registry.'));
      } else {
        await amenagementAPI.createPlace(payload);
        toast.success(t('Place déclarée dans le référentiel national.', 'Place declared in the national registry.'));
      }
      setOuvert(false);
      setEdition(null);
      rafraichir();
    } catch (err) {
      toast.error(messageServeur(err, t('Enregistrement refusé.', 'Recording refused.')));
    } finally {
      setEnCours(false);
    }
  };

  /** Sortir du périmètre n'efface rien : référentiel partagé, on désactive. */
  const desactiver = async (ligne: PlacePortuaire) => {
    if (!peutCorriger) return;
    setEnCours(true);
    try {
      await amenagementAPI.updatePlace(ligne.id, { est_actif: false });
      toast.success(
        t(
          `« ${ligne.nom || ligne.code} » est sortie du périmètre. La référence reste consultable, rien n'est effacé.`,
          `“${ligne.nom || ligne.code}” is out of perimeter. The reference stays readable, nothing is erased.`,
        ),
      );
      rafraichir();
    } catch (err) {
      toast.error(messageServeur(err, t('Retrait refusé.', 'Withdrawal refused.')));
    } finally {
      setEnCours(false);
    }
  };

  const reactiver = async (ligne: PlacePortuaire) => {
    if (!peutCorriger) return;
    setEnCours(true);
    try {
      await amenagementAPI.updatePlace(ligne.id, { est_actif: true });
      toast.success(t('Place réintégrée dans le périmètre.', 'Place back in perimeter.'));
      rafraichir();
    } catch (err) {
      toast.error(messageServeur(err, t('Réintégration refusée.', 'Reactivation refused.')));
    } finally {
      setEnCours(false);
    }
  };

  if (!peutLire) {
    return (
      <div className="flex items-start gap-3 rounded-2xl border border-slate-700 bg-slate-900/70 p-4">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <p className="text-sm text-slate-300 leading-relaxed">
          {t(
            'La lecture du référentiel national des places est soumise à la permission amenagement.place.read. Sans elle, aucun registre du département ne pourra rattacher une ligne à une place portuaire : demandez cette habilitation à l’administrateur de votre tenant.',
            'Reading the national port-place registry requires the amenagement.place.read permission. Without it no register of the department can attach a line to a port place: request this accreditation from your tenant administrator.',
          )}
        </p>
      </div>
    );
  }

  const lignes = places.data || [];
  const entreesTypePort = nomenclatures.data?.type_port || [];

  return (
    <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="flex items-center gap-2 text-sm font-bold text-slate-100">
            <MapPin className="w-4 h-4 text-cyan-300" />
            {t('Référentiel des places portuaires', 'Port places registry')}
            <span className="text-xs font-normal text-slate-400">({lignes.length})</span>
          </h2>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-400 max-w-3xl">
            {t(
              'Table nationale ports_cameroun, alimentée par les agents depuis les documents officiels. Le logiciel ne préremplit aucune place : Douala, Kribi et Limbé n’apparaîtront qu’une fois déclarées ici. Une valeur absente reste « non enregistré », jamais zéro ni une estimation.',
              'National table ports_cameroun, fed by officers from official documents. The software prefills no place: Douala, Kribi and Limbé will only appear once declared here. A missing value stays “not recorded”, never zero nor an estimate.',
            )}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {peutDeclarer && !ouvert && (
            <button
              type="button"
              onClick={() => ouvrir(null)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-700 hover:bg-cyan-600 text-cyan-50 text-xs font-semibold"
            >
              <Plus className="w-3.5 h-3.5" />
              {t('Déclarer une place', 'Declare a place')}
            </button>
          )}
        </div>
      </header>

      {!peutDeclarer && !peutCorriger && (
        <p className="mt-2 text-[11px] text-amber-300/90">
          {t(
            'Votre rôle consulte le référentiel mais ne peut pas l’alimenter (amenagement.place.create / .modify).',
            'Your role reads the registry but cannot feed it (amenagement.place.create / .modify).',
          )}
        </p>
      )}

      {places.loading && !places.data ? (
        <div className="mt-3">
          <DataLoadingState rows={3} label={t('Chargement du référentiel national…', 'Loading national registry…')} />
        </div>
      ) : places.error ? (
        <div className="mt-3">
          <DataErrorState error={places.error} onRetry={() => places.refetch()} />
        </div>
      ) : lignes.length === 0 && !ouvert ? (
        <div className="mt-3">
          <DataEmptyState
            title={t('Référentiel vide', 'Empty registry')}
            description={t(
              'Aucune place portuaire n’est encore déclarée dans ports_cameroun. Tant que ce n’est pas fait, les neufs registres du département ne peuvent rattacher aucune ligne à une place : c’est le premier acte du service, et il se fait à partir des textes officiels, pas d’une liste proposée par le logiciel.',
              'No port place is declared yet in ports_cameroun. Until this is done, the department’s nine registers cannot attach any line to a place: this is the service’s first act, and it is done from official texts, not from a list suggested by the software.',
            )}
            actionLabel={peutDeclarer ? t('Déclarer la première place', 'Declare the first place') : undefined}
            onAction={peutDeclarer ? () => ouvrir(null) : undefined}
          />
        </div>
      ) : (
        <div className="mt-3 -mx-1 overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-[10px] uppercase tracking-wide text-slate-400 border-b border-slate-800">
                <th className="px-2 py-2 font-semibold">{t('Code', 'Code')}</th>
                {COLONNES_PLACE.map((c) => (
                  <th key={String(c.name)} className="px-2 py-2 font-semibold whitespace-nowrap">
                    {lang === 'en' ? c.labelEn : c.label}
                  </th>
                ))}
                <th className="px-2 py-2 font-semibold text-right">{t('Actes', 'Actions')}</th>
              </tr>
            </thead>
            <tbody>
              {lignes.map((ligne) => (
                <tr
                  key={ligne.id}
                  className={`border-b border-slate-800/70 ${ligne.est_actif ? '' : 'opacity-50'}`}
                >
                  <td className="px-2 py-2">
                    <span className="font-mono text-[11px] text-cyan-200">{ligne.code}</span>
                    {!ligne.est_actif && (
                      <span className="ml-1.5 text-[9px] uppercase text-slate-500">
                        {t('hors périmètre', 'out of perimeter')}
                      </span>
                    )}
                  </td>
                  {COLONNES_PLACE.map((c) => {
                    const rendu = cellulePlace(c, ligne, lang, nomenclatures.data);
                    return (
                      <td
                        key={String(c.name)}
                        className={`px-2 py-2 whitespace-nowrap ${rendu.manquant ? 'text-slate-500 italic' : 'text-slate-200'}`}
                      >
                        {rendu.texte}
                      </td>
                    );
                  })}
                  <td className="px-2 py-2 text-right whitespace-nowrap">
                    {peutCorriger && (
                      <>
                        <button
                          type="button"
                          disabled={enCours}
                          onClick={() => ouvrir(ligne)}
                          className="inline-flex items-center gap-1 rounded-lg bg-slate-800 hover:bg-slate-700 px-2 py-1 text-[11px] font-semibold text-slate-200 disabled:opacity-50"
                        >
                          <Pencil className="w-3 h-3" />
                          {t('Corriger', 'Correct')}
                        </button>
                        {ligne.est_actif ? (
                          <button
                            type="button"
                            disabled={enCours}
                            onClick={() => desactiver(ligne)}
                            className="ml-1 inline-flex items-center gap-1 rounded-lg bg-slate-800 hover:bg-rose-900/50 px-2 py-1 text-[11px] font-semibold text-slate-200 disabled:opacity-50"
                          >
                            <X className="w-3 h-3" />
                            {t('Sortir du périmètre', 'Out of perimeter')}
                          </button>
                        ) : (
                          <button
                            type="button"
                            disabled={enCours}
                            onClick={() => reactiver(ligne)}
                            className="ml-1 rounded-lg bg-slate-800 hover:bg-slate-700 px-2 py-1 text-[11px] font-semibold text-slate-200 disabled:opacity-50"
                          >
                            {t('Réintégrer', 'Reactivate')}
                          </button>
                        )}
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="mt-2 text-[10px] leading-relaxed text-slate-500">
        {t(
          'Une place ne se supprime pas : la table est partagée avec les terminaux, la tarification et les périmètres d’autres modules. Sortir du périmètre laisse la référence intacte et consultable.',
          'A place is never deleted: the table is shared with terminals, pricing and perimeters of other modules. Going out of perimeter leaves the reference intact and readable.',
        )}
      </p>

      {ouvert && (
        <div className="mt-4 rounded-2xl border border-cyan-900/60 bg-cyan-950/20 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-bold text-cyan-100">
              {edition
                ? t(`Corriger « ${edition.nom || edition.code} »`, `Correct “${edition.nom || edition.code}”`)
                : t('Déclarer une place dans le référentiel national', 'Declare a place in the national registry')}
            </h3>
            <button
              type="button"
              onClick={() => {
                setOuvert(false);
                setEdition(null);
              }}
              className="rounded-lg bg-slate-800 hover:bg-slate-700 px-2 py-1 text-[11px] font-semibold text-slate-300"
            >
              {t('Fermer', 'Close')}
            </button>
          </div>

          <p className="mt-1 text-[11px] leading-relaxed text-cyan-100/80">
            {t(
              'Recopiez le document officiel : le code, la dénomination et la nature sont exigés par le serveur, tout le reste peut rester vide et s’affichera « non enregistré ». Rien n’est complété automatiquement.',
              'Copy the official document: code, name and type are required by the server, everything else may stay blank and will read “not recorded”. Nothing is completed automatically.',
            )}
          </p>
          {entreesTypePort.length > 0 && (
            <p className="mt-1 text-[10px] text-slate-400">
              {t('Valeurs admises', 'Accepted values')} :{' '}
              {entreesTypePort.map((e) => humaniser(e.valeur)).join(', ')}
            </p>
          )}

          <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            {CHAMPS_PLACE.map((c) => {
              const lectureSeule = Boolean(c.lectureSeuleEdition && edition);
              const classe =
                'w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-600/60 disabled:opacity-50';
              const entrees = c.nomenclature ? nomenclatures.data?.[c.nomenclature] || [] : [];
              const aide = lang === 'en' ? c.aideEn || c.aide : c.aide;
              return (
                <label key={c.name} className={c.type === 'zone' ? 'sm:col-span-2 block' : 'block'}>
                  <span className="block text-xs font-semibold text-slate-300 mb-1.5">
                    {lang === 'en' ? c.labelEn : c.label}
                    {c.unite ? <span className="text-slate-500"> ({c.unite})</span> : null}
                    {c.requis && !lectureSeule && <span className="text-amber-400"> *</span>}
                  </span>
                  {c.type === 'select' ? (
                    <select
                      value={saisie[c.name] ?? ''}
                      disabled={lectureSeule || nomenclatures.loading}
                      onChange={(e) => setSaisie((s) => ({ ...s, [c.name]: e.target.value }))}
                      className={classe}
                    >
                      <option value="">{tManquant(lang)}</option>
                      {entrees.map((e) => (
                        <option key={e.code} value={e.valeur}>
                          {humaniser(e.valeur)}
                        </option>
                      ))}
                      {entrees.length === 0 && (
                        <option value="" disabled>
                          {t('Nomenclature indisponible', 'Nomenclature unavailable')}
                        </option>
                      )}
                    </select>
                  ) : c.type === 'booleen' ? (
                    <select
                      value={saisie[c.name] ?? ''}
                      onChange={(e) => setSaisie((s) => ({ ...s, [c.name]: e.target.value }))}
                      className={classe}
                    >
                      <option value="">{tManquant(lang)}</option>
                      <option value="oui">{lang === 'en' ? 'Yes' : 'Oui'}</option>
                      <option value="non">{lang === 'en' ? 'No' : 'Non'}</option>
                    </select>
                  ) : c.type === 'zone' ? (
                    <textarea
                      rows={3}
                      value={saisie[c.name] ?? ''}
                      onChange={(e) => setSaisie((s) => ({ ...s, [c.name]: e.target.value }))}
                      className={classe}
                      placeholder={aide || ''}
                    />
                  ) : (
                    <input
                      type={c.type === 'date' ? 'date' : c.type === 'nombre' ? 'number' : 'text'}
                      value={saisie[c.name] ?? ''}
                      disabled={lectureSeule}
                      step={c.type === 'nombre' ? '0.01' : undefined}
                      onChange={(e) => setSaisie((s) => ({ ...s, [c.name]: e.target.value }))}
                      className={classe}
                      placeholder={lectureSeule ? t('Immuable après déclaration', 'Immutable after declaration') : ''}
                    />
                  )}
                  {aide && <span className="mt-1 block text-[11px] leading-relaxed text-slate-400">{aide}</span>}
                </label>
              );
            })}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              type="button"
              disabled={enCours}
              onClick={enregistrer}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-cyan-700 hover:bg-cyan-600 text-cyan-50 text-xs font-bold disabled:opacity-50"
            >
              <Plus className="w-3.5 h-3.5" />
              {enCours
                ? t('Enregistrement…', 'Recording…')
                : edition
                  ? t('Enregistrer la correction', 'Save correction')
                  : t('Déclarer la place', 'Declare the place')}
            </button>
            <span className="text-[11px] text-slate-400">
              {requisManquants.length
                ? t(`Serveur exige : ${requisManquants.join(', ')}`, `Server requires: ${requisManquants.join(', ')}`)
                : t('Un champ vide ne sera pas envoyé : la colonne restera NULL.', 'An empty field will not be sent: the column stays NULL.')}
            </span>
          </div>
        </div>
      )}
    </section>
  );
}

/** Reprise locale de l'affichage d'une date, pour le cas où la colonne serait
 *  absente du format registre (une place n'est pas une ligne de registre). */
export function datePlace(iso: string | null, lang: 'fr' | 'en'): string {
  if (estAbsent(iso) || !iso) return tManquant(lang);
  return formaterDate(iso, lang);
}
