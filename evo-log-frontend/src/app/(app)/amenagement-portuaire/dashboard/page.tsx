'use client';

/**
 * Centre de pilotage du département Aménagement portuaire & Domaine public.
 *
 * Ce que cette page sait faire, et ce qu'elle refuse de faire :
 *  - elle n'affiche QUE ce que /api/v1/amenagement-portuaire/synthese agrège
 *    depuis les lignes réellement saisies : aucun pourcentage, aucun budget et
 *    aucune capacité ne sont estimés côté navigateur ;
 *  - un agrégat d'argent NULL reste écrit « aucune saisie » : afficher 0 ferait
 *    croire à un budget soldé alors qu'aucune ligne n'est enregistrée ;
 *  - le périmètre (Douala, Kribi, Limbé) est lu sur /places, référentiel
 *    national : si le serveur ne connaît pas encore une place, la page ne la
 *    nomme pas ;
 *  - les compteurs à 0 sont un fait (« 0 titre échu »), pas un vide : ils
 *    restent affichés tels quels.
 */
import React, { useCallback, useState } from 'react';
import Link from 'next/link';
import { ArrowUpRight, Info, RefreshCw, ShieldAlert } from 'lucide-react';

import ModuleLayout from '@/components/layout/ModuleLayout';
import { DataEmptyState, DataErrorState, DataLoadingState } from '@/components/shared/StatePanels';
import { useApi } from '@/hooks/useApi';
import { useCan } from '@/hooks/useCan';
import { useSettings } from '@/components/layout/SettingsProvider';
import { amenagementAPI } from '@/lib/api-client';
import { getRouteFromTCode } from '@/utils/tcodeLookup';

import type { PlacePortuaire } from '@/components/amenagement-portuaire/typesRegistre';
import { REGISTRES_AMENAGEMENT } from '@/components/amenagement-portuaire/registres';
import { estAbsent, formaterMesure, formaterMontant } from '@/components/amenagement-portuaire/formatRegistre';

/** Réponse exacte de GET /synthese (voir app/routers/v1/amenagement_portuaire.py).
 *  Déclarée ici pour être lue, pas pour être complétée : toute clé absente
 *  s'affiche comme non servie. */
interface Synthese {
  perimetre?: {
    port_id?: number | null;
    places?: string[];
    explication?: string;
  };
  schemas_directeurs?: { actifs?: number; approuves?: number; en_elaboration?: number; a_reviser?: number };
  projets?: {
    total?: number;
    en_cours?: number;
    sans_fiche_technique?: number;
    cout_previsionnel_total_xaf?: number | null;
    cout_reel_total_xaf?: number | null;
    suivi_financier_complet?: boolean;
  };
  passation?: {
    marches_total?: number;
    marches_en_execution?: number;
    montant_engage_xaf?: number | null;
    en_attente_colife?: number;
  };
  domaine?: {
    titres_actifs?: number;
    titres_expire?: number;
    concessions_en_vigueur?: number;
    concessions_echeance_12_mois?: number;
  };
  patrimoine?: {
    ouvrages_inventories?: number;
    operationnels?: number;
    degrades_ou_hors_service?: number;
    sans_date_inspection?: number;
  };
  dragage?: { campagnes?: number; volume_total_releve_m3?: number | null; sans_leve_apres?: number };
  conformite?: {
    dossiers_total?: number;
    en_attente_de_decision?: number;
    accordees?: number;
    expirees?: number;
  };
}

/** Une ligne d'indicateur : un compteur (fait brut), une mesure ou un montant
 *  (peut être non saisi). `valeur` vient du serveur, jamais d'un calcul local. */
type ValeurIndicateur =
  | { genre: 'compteur'; valeur?: number }
  | { genre: 'mesure'; valeur?: number | null; unite: string }
  | { genre: 'montant'; valeur?: number | null };

export default function AmenagementPortuaireDashboardPage() {
  const { language } = useSettings();
  const lang: 'fr' | 'en' = language === 'en' ? 'en' : 'fr';
  const t = (fr: string, en: string) => (lang === 'en' ? en : fr);
  const can = useCan();

  // /synthese est servis sous la permission du portefeuille de projets : c'est
  // la route qui l'annonce, pas cette page qui en décide.
  const peutPiloter = can('amenagement.projet.read');

  /* Place portuaire filtrant la synthèse. Vide = tout le périmètre du
     département. Les options viennent de /places, aucune n'est écrite ici. */
  const [portId, setPortId] = useState('');
  const portCourant = portId;

  const places = useApi<PlacePortuaire[]>(async () => {
    const brut = (await amenagementAPI.getPlaces()).data as { data?: PlacePortuaire[] };
    return Array.isArray(brut?.data) ? brut.data : [];
  });

  const synthese = useApi<Synthese | null>(
    async () => (await amenagementAPI.getSynthese(portCourant ? Number(portCourant) : undefined)).data as Synthese,
  );

  const refreschir = useCallback(() => {
    synthese.refetch();
    places.refetch();
  }, [synthese, places]);

  /** Rend un indicateur : un compteur à 0 reste un chiffre, une mesure ou un
   *  montant non saisi reste un manquant explicite. */
  const rendreValeur = (ind: ValeurIndicateur): { texte: string; absent: boolean } => {
    if (ind.genre === 'montant') {
      if (estAbsent(ind.valeur ?? null)) {
        return { texte: t('aucune saisie', 'no entry'), absent: true };
      }
      return { texte: formaterMontant(ind.valeur ?? null, lang), absent: false };
    }
    if (ind.genre === 'mesure') {
      if (estAbsent(ind.valeur ?? null)) {
        return { texte: t('aucune saisie', 'no entry'), absent: true };
      }
      return { texte: formaterMesure(ind.valeur ?? null, ind.unite, lang), absent: false };
    }
    return { texte: String(ind.valeur ?? 0), absent: false };
  };

  if (!peutPiloter) {
    return (
      <ModuleLayout
        title={t('Centre de pilotage aménagement', 'Development control centre')}
        description={t(
          'Vue consolidée du domaine, de la programmation et des ouvrages de vos places portuaires.',
          'Consolidated view of the domain, programming and structures of your port places.',
        )}
      >
        <div className="flex items-start gap-3 rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-sm text-slate-300 leading-relaxed">
            {t(
              'Votre rôle ne dispose pas de la permission amenagement.projet.read, celle qu\u2019exige la route /synthese. Les registres du département restent accessibles selon vos propres habilitations : demandez cette extension à l\u2019administrateur de votre tenant.',
              'Your role does not hold the amenagement.projet.read permission required by the /synthese route. The department registers remain reachable under your own accreditations: request this extension from your tenant administrator.',
            )}
          </p>
        </div>
        <GrilleRegistres can={can} t={t} lang={lang} />
      </ModuleLayout>
    );
  }

  const s = synthese.data || {};

  return (
    <ModuleLayout
      title={t('Centre de pilotage aménagement', 'Development control centre')}
      description={t(
        'Domaine public, schémas directeurs, programmation budgétaire, marchés, titres, concessions, ouvrages, dragage et autorisations — agrégé uniquement à partir des lignes saisies.',
        'Public domain, master plans, budget programming, contracts, titles, concessions, structures, dredging and permits — aggregated only from recorded lines.',
      )}
      help={t(
        'Un chiffre affiché « aucune saisie » signifie que la colonne est vide en base, pas que le montant est nul. La synthèse n\u2019additionne que les montants réellement enregistrés.',
        'A figure reading “no entry” means the column is empty in database, not that the amount is zero. The synthesis adds up only amounts actually recorded.',
      )}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-400 uppercase">
              {t('Place', 'Port place')}
            </span>
            <select
              value={portId}
              onChange={(e) => {
                setPortId(e.target.value);
                synthese.refetch();
              }}
              className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-600/60"
            >
              <option value="">{t('Tout le département', 'Whole department')}</option>
              {(places.data || []).map((p) => (
                <option key={p.id} value={String(p.id)}>
                  {p.nom || p.code}
                  {p.code ? ` (${p.code})` : ''}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={refreschir}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${synthese.loading || places.loading ? 'animate-spin' : ''}`} />
            {t('Actualiser', 'Refresh')}
          </button>
        </div>
      }
    >
      {synthese.loading && !synthese.data ? (
        <DataLoadingState rows={4} label={t('Chargement de la synthèse du département…', 'Loading department synthesis…')} />
      ) : synthese.error ? (
        <DataErrorState error={synthese.error} onRetry={() => synthese.refetch()} />
      ) : (
        <div className="space-y-5">
          {/* Périmètre : codes déclarés par le serveur, noms résolus depuis le
              référentiel national. Rien n'est inventé si une place manque. */}
          <div className="rounded-2xl border border-cyan-900/60 bg-cyan-950/30 p-4">
            <div className="flex items-start gap-2">
              <Info className="w-4 h-4 text-cyan-300 shrink-0 mt-0.5" />
              <div className="min-w-0">
                <p className="text-xs font-semibold text-cyan-200 uppercase tracking-wide">
                  {t('Périmètre d’étude du département', 'Department study perimeter')}
                </p>
                <p className="mt-1 text-xs text-cyan-100/80 leading-relaxed">
                  {(s.perimetre?.places || [])
                    .map((code) => {
                      const p = (places.data || []).find((place) => place.code === code);
                      return p ? p.nom || p.code : code;
                    })
                    .join(' · ') || t('Aucune place déclarée par le serveur.', 'No place declared by the server.')}
                </p>
                {s.perimetre?.explication && (
                  <p className="mt-1 text-[11px] text-cyan-200/70 leading-relaxed italic">
                    {s.perimetre.explication}
                  </p>
                )}
              </div>
            </div>
          </div>

          {synthese.isEmpty && (
            <DataEmptyState
              title={t('Aucune saisie dans le département', 'No entry in the department')}
              description={t(
                'Les registres sont vides pour ce périmètre : la synthèse affiche des compteurs à zéro et des montants non saisis, elle n’invente aucune donnée de démarrage.',
                'The registers are empty for this perimeter: the synthesis shows zero counters and unrecorded amounts, it invents no starting data.',
              )}
            />
          )}

          <Bloc
            titre={t('Schémas directeurs', 'Master plans')}
            tcode="KAMT_SCH"
            indicateurs={[
              { libelle: t('Actifs', 'Active'), ind: { genre: 'compteur', valeur: s.schemas_directeurs?.actifs } },
              { libelle: t('Approuvés', 'Approved'), ind: { genre: 'compteur', valeur: s.schemas_directeurs?.approuves } },
              { libelle: t('En élaboration', 'In drafting'), ind: { genre: 'compteur', valeur: s.schemas_directeurs?.en_elaboration } },
              { libelle: t('Échéance de révision dépassée', 'Review deadline passed'), ind: { genre: 'compteur', valeur: s.schemas_directeurs?.a_reviser } },
            ]}
            t={t}
            rendreValeur={rendreValeur}
          />

          <Bloc
            titre={t('Projets d’aménagement', 'Development projects')}
            tcode="KAMT_PRJ"
            indicateurs={[
              { libelle: t('Au portefeuille', 'In portfolio'), ind: { genre: 'compteur', valeur: s.projets?.total } },
              { libelle: t('En cours', 'Ongoing'), ind: { genre: 'compteur', valeur: s.projets?.en_cours } },
              { libelle: t('Sans fiche technique', 'Without technical sheet'), ind: { genre: 'compteur', valeur: s.projets?.sans_fiche_technique } },
              { libelle: t('Coût prévisionnel', 'Planned cost'), ind: { genre: 'montant', valeur: s.projets?.cout_previsionnel_total_xaf } },
              { libelle: t('Coût réel', 'Actual cost'), ind: { genre: 'montant', valeur: s.projets?.cout_reel_total_xaf } },
            ]}
            note={
              s.projets?.suivi_financier_complet === false
                ? t(
                    'Le suivi financier n’est complet que si les deux colonnes (prévisionnel et réel) sont saisies : ici l’une des deux reste vide.',
                    'Financial tracking is complete only when both columns (planned and actual) are recorded: one of them is still blank.',
                  )
                : undefined
            }
            t={t}
            rendreValeur={rendreValeur}
          />

          <Bloc
            titre={t('Passation des marchés', 'Contract award')}
            tcode="KAMT_MCH"
            indicateurs={[
              { libelle: t('Marchés inscrits', 'Registered contracts'), ind: { genre: 'compteur', valeur: s.passation?.marches_total } },
              { libelle: t('En exécution', 'In execution'), ind: { genre: 'compteur', valeur: s.passation?.marches_en_execution } },
              { libelle: t('En attente d’avis COLIFE/CIP', 'Awaiting COLIFE/CIP advice'), ind: { genre: 'compteur', valeur: s.passation?.en_attente_colife } },
              { libelle: t('Montant engagé', 'Committed amount'), ind: { genre: 'montant', valeur: s.passation?.montant_engage_xaf } },
            ]}
            t={t}
            rendreValeur={rendreValeur}
          />

          <Bloc
            titre={t('Domaine public', 'Public domain')}
            lien="/amenagement-portuaire/titres-domaniaux"
            indicateurs={[
              { libelle: t('Titres en vigueur', 'Valid titles'), ind: { genre: 'compteur', valeur: s.domaine?.titres_actifs } },
              { libelle: t('Titres échus', 'Expired titles'), ind: { genre: 'compteur', valeur: s.domaine?.titres_expire } },
              { libelle: t('Concessions en vigueur', 'Active concessions'), ind: { genre: 'compteur', valeur: s.domaine?.concessions_en_vigueur } },
              { libelle: t('Concessions à échéance sous 12 mois', 'Concessions due within 12 months'), ind: { genre: 'compteur', valeur: s.domaine?.concessions_echeance_12_mois } },
            ]}
            t={t}
            rendreValeur={rendreValeur}
          />

          <Bloc
            titre={t('Patrimoine bâti', 'Built assets')}
            lien="/amenagement-portuaire/infrastructures"
            indicateurs={[
              { libelle: t('Ouvrages inventoriés', 'Inventoried structures'), ind: { genre: 'compteur', valeur: s.patrimoine?.ouvrages_inventories } },
              { libelle: t('Opérationnels', 'Operational'), ind: { genre: 'compteur', valeur: s.patrimoine?.operationnels } },
              { libelle: t('Dégradés ou hors service', 'Degraded or out of service'), ind: { genre: 'compteur', valeur: s.patrimoine?.degrades_ou_hors_service } },
              { libelle: t('Sans date d’inspection', 'Without inspection date'), ind: { genre: 'compteur', valeur: s.patrimoine?.sans_date_inspection } },
            ]}
            t={t}
            rendreValeur={rendreValeur}
          />

          <Bloc
            titre={t('Dragage & profondeurs', 'Dredging & depths')}
            lien="/amenagement-portuaire/dragage"
            indicateurs={[
              { libelle: t('Campagnes', 'Campaigns'), ind: { genre: 'compteur', valeur: s.dragage?.campagnes } },
              { libelle: t('Volume relevé', 'Surveyed volume'), ind: { genre: 'mesure', valeur: s.dragage?.volume_total_releve_m3, unite: 'm³' } },
              { libelle: t('Sans levé après travaux', 'Without post-work survey'), ind: { genre: 'compteur', valeur: s.dragage?.sans_leve_apres } },
            ]}
            t={t}
            rendreValeur={rendreValeur}
          />

          <Bloc
            titre={t('Conformité administrative', 'Administrative compliance')}
            lien="/amenagement-portuaire/autorisations"
            indicateurs={[
              { libelle: t('Dossiers', 'Files'), ind: { genre: 'compteur', valeur: s.conformite?.dossiers_total } },
              { libelle: t('En attente de décision', 'Awaiting decision'), ind: { genre: 'compteur', valeur: s.conformite?.en_attente_de_decision } },
              { libelle: t('Accordées', 'Granted'), ind: { genre: 'compteur', valeur: s.conformite?.accordees } },
              { libelle: t('Expirées', 'Expired'), ind: { genre: 'compteur', valeur: s.conformite?.expirees } },
            ]}
            t={t}
            rendreValeur={rendreValeur}
          />

          <GrilleRegistres can={can} t={t} lang={lang} />
        </div>
      )}
    </ModuleLayout>
  );
}

/* ------------------------------ sous-blocs -------------------------------- */

function Bloc({
  titre,
  tcode,
  indicateurs,
  note,
  t,
  rendreValeur,
}: {
  titre: string;
  /** Le registre cible est désigné par son T-Code, résolu dans le registre
   *  canonique des routes (utils/tcodeLookup) : aucun chemin n'est retapé ici. */
  tcode: string;
  indicateurs: { libelle: string; ind: ValeurIndicateur }[];
  note?: string;
  t: (fr: string, en: string) => string;
  rendreValeur: (ind: ValeurIndicateur) => { texte: string; absent: boolean };
}) {
  return (
    <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-bold text-slate-100">{titre}</h2>
        <Link
          href={getRouteFromTCode(tcode)}
          className="inline-flex items-center gap-1 text-[11px] font-semibold text-cyan-300 hover:text-cyan-200"
        >
          {t('Ouvrir le registre', 'Open register')}
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
      <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {indicateurs.map((it) => {
          const rendu = rendreValeur(it.ind);
          return (
            <div key={it.libelle} className="rounded-xl border border-slate-800 bg-slate-950/50 px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-wide text-slate-400 leading-tight">{it.libelle}</p>
              <p
                className={`mt-1 text-base font-bold ${
                  rendu.absent ? 'text-slate-500 text-xs font-semibold' : 'text-cyan-200'
                }`}
              >
                {rendu.texte}
              </p>
            </div>
          );
        })}
      </div>
      {note && (
        <p className="mt-3 text-[11px] leading-relaxed text-amber-300/90">{note}</p>
      )}
    </section>
  );
}

/** Les neuf registres, déclarés dans registres.ts (aucun chemin dupliqué ici).
 *  Une carte sans habilitation de lecture reste visible mais dit précisément
 *  ce qui manque, plutôt que d'ouvrir un écran qui refusera la donnée. */
function GrilleRegistres({
  can,
  t,
  lang,
}: {
  can: (code: string) => boolean;
  t: (fr: string, en: string) => string;
  lang: 'fr' | 'en';
}) {
  const entrees = Object.entries(REGISTRES_AMENAGEMENT) as [string, (typeof REGISTRES_AMENAGEMENT)[keyof typeof REGISTRES_AMENAGEMENT]][];
  return (
    <section>
      <h2 className="text-sm font-bold text-slate-100 mb-3">
        {t('Registres du département', 'Department registers')}
        <span className="ml-2 text-xs font-normal text-slate-400">({entrees.length})</span>
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {entrees.map(([segment, config]) => {
          const Icon = config.icon;
          const autorise = can(`amenagement.${config.permSousModule}.read`);
          return (
            <Link
              key={segment}
              href={`/amenagement-portuaire/${segment}`}
              className={`group rounded-2xl border p-4 transition ${
                autorise
                  ? 'border-slate-800 bg-slate-900/60 hover:border-cyan-700/70 hover:bg-slate-900'
                  : 'border-slate-800/60 bg-slate-950/40'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className={`p-2 rounded-xl ${autorise ? 'bg-cyan-700 text-cyan-50' : 'bg-slate-800 text-slate-400'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="font-mono text-[10px] text-slate-500 border border-slate-800 rounded px-1.5 py-0.5">
                  {config.tcode}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-semibold text-slate-100 group-hover:text-cyan-200">
                {lang === 'en' ? config.titreEn : config.titre}
              </h3>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400 line-clamp-2">
                {lang === 'en' ? config.descriptionEn : config.description}
              </p>
              {!autorise && (
                <p className="mt-2 text-[10px] font-semibold text-amber-300/90">
                  {t(
                    `Lecture soumise à ${`amenagement.${config.permSousModule}.read`}`,
                    `Reading requires amenagement.${config.permSousModule}.read`,
                  )}
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </section>
  );
}
