'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { metierAPI } from '@/lib/api-client';
import { RefreshCw } from 'lucide-react';

type Data = Record<string, unknown>;

interface Widget {
  titre: string;
  fetcher: () => Promise<{ data: Data }>;
  render: (d: Data) => React.ReactNode;
}

interface Section {
  nom: string;
  widgets: Widget[];
}

const nf = (v: unknown) => {
  if (v === null || v === undefined) return '—';
  const n = Number(v);
  return Number.isFinite(n) ? n.toLocaleString('fr-FR') : String(v);
};
const isNote = (d: Data) => typeof d.note === 'string';
const Empty = ({ d }: { d: Data }) =>
  isNote(d) ? <p className="text-sm text-gray-500">{String(d.note)}</p> : <p className="text-sm text-gray-400">—</p>;
const Big = ({ value, label }: { value: unknown; label: string }) => (
  <>
    <p className="text-2xl font-bold">{nf(value)}</p>
    <p className="text-xs text-gray-500">{label}</p>
  </>
);

const SECTIONS: Section[] = [
  {
    nom: 'Finance & Comptabilité',
    widgets: [
      { titre: 'Trésorerie prévisionnelle', fetcher: () => metierAPI.getFinancePrevisions(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.solde_net_previsionnel_xaf} label={`XAF net — ${nf(d.risques_decouvert)} risque(s)`} /> },
      { titre: 'Affacturage', fetcher: () => metierAPI.getFinanceAffacturage(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.avances_en_cours_xaf} label={`XAF en cours — ${nf(d.echus_non_rembourses)} échu(s)`} /> },
      { titre: 'Budgetaire', fetcher: () => metierAPI.getControleBudgetaire(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.depassements ?? d.total ?? 0} label="dépassements budgétaires" /> },
      { titre: 'Contre-passations', fetcher: () => metierAPI.getComptaContrePassations(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.ecritures ?? 0} label="écritures de contre-passation" /> },
      { titre: 'Indicateurs financiers', fetcher: () => metierAPI.getIndicateursFinanciers(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.sous_objectif} label={`sous objectif / ${nf(d.indicateurs_total)}`} /> },
    ],
  },
  {
    nom: 'Paie & RH',
    widgets: [
      { titre: 'Masse salariale', fetcher: () => metierAPI.getPaieCumuls(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.masse_brute_xaf} label={`XAF brut — ${nf(d.employes)} salariés`} /> },
      { titre: 'Formation', fetcher: () => metierAPI.getRhFormation(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.taux_realisation_pct} label={`% réalisation — ${nf(Array.isArray(d.incomplets) ? d.incomplets.length : 0)} incomplet(s)`} /> },
      { titre: 'Discipline', fetcher: () => metierAPI.getRhDiscipline(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.actives} label={`sanctions actives / ${nf(d.sanctions_total)}`} /> },
      { titre: 'Certifications', fetcher: () => metierAPI.getFormationCertifications(30),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.expires ?? d.total ?? 0} label="expirées ou à renouveler (30 j)" /> },
      { titre: 'Recrutement', fetcher: () => metierAPI.getRecrutementPipeline(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? Object.keys(d).length} label="candidatures en pipeline" /> },
      { titre: 'Congés', fetcher: () => metierAPI.getRhConges('__none__').catch(() => ({ data: {} })),
        render: () => <Link href="/metier/calculs" className="text-sm text-blue-600 hover:underline">Rechercher par collaborateur →</Link> },
    ],
  },
  {
    nom: 'Transport & Logistique',
    widgets: [
      { titre: 'Cuves en alerte', fetcher: () => metierAPI.getCuvesEnAlerte(20),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.cuves_en_alerte ?? d.total ?? 0} label="sous 20 %" /> },
      { titre: 'Tournees', fetcher: () => metierAPI.getTransportTournees(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.tournees_total} label={`tournées — ${nf(d.km_total)} km`} /> },
      { titre: 'DG non conformes', fetcher: () => metierAPI.getTransportDg(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.non_conformes ?? d.total ?? 0} label="marchandises dangereuses" /> },
      { titre: 'Repos insuffisants', fetcher: () => metierAPI.getTransportRepos(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.chauffeurs ?? 0} label="chauffeurs" /> },
      { titre: 'Pneus à remplacer', fetcher: () => metierAPI.getParcPneus(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.pneus ?? 0} label="sous 1,6 mm" /> },
      { titre: 'Cycle conteneur', fetcher: () => metierAPI.getConteneurCycle(0).catch(() => ({ data: { note: 'Voir /metier/calculs' } })),
        render: () => <Link href="/metier/calculs" className="text-sm text-blue-600 hover:underline">Ouvrir l'analyse →</Link> },
      { titre: 'Coursier', fetcher: () => metierAPI.getCoursierPerformance('—').catch(() => ({ data: { note: 'Voir /metier/calculs' } })),
        render: () => <Link href="/metier/calculs" className="text-sm text-blue-600 hover:underline">Ouvrir l'analyse →</Link> },
      { titre: 'Fluvial navigabilité', fetcher: () => metierAPI.getFluvialNavigabilite(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.biefs_restent ?? d.total ?? 0} label="biefs navigables" /> },
    ],
  },
  {
    nom: 'Magasin & Douane',
    widgets: [
      { titre: 'Écarts inventaire', fetcher: () => metierAPI.getMagasinEcarts(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.ecarts} label={`sur ${nf(d.lignes_total)} lignes`} /> },
      { titre: 'Déclarations douane', fetcher: () => metierAPI.getDouaneAttente(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.declarations ?? 0} label="en attente" /> },
      { titre: 'Transit conformité', fetcher: () => metierAPI.getTransitConformite(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.taux_conformite ?? d.total ?? 0} label="taux / inspections" /> },
      { titre: 'Corrosion pipeline', fetcher: () => metierAPI.getPipelineCorrosion('—', 0).catch(() => ({ data: { note: 'Voir /metier/calculs' } })),
        render: () => <Link href="/metier/calculs" className="text-sm text-blue-600 hover:underline">Ouvrir l'analyse →</Link> },
      { titre: 'Valorisation douanière', fetcher: () => metierAPI.getDouaneValorisation(0).catch(() => ({ data: { note: 'Voir /metier/calculs' } })),
        render: () => <Link href="/metier/calculs" className="text-sm text-blue-600 hover:underline">Ouvrir l'analyse →</Link> },
    ],
  },
  {
    nom: 'QHSE & Sécurité',
    widgets: [
      { titre: 'Dépassements normes', fetcher: () => metierAPI.getQhseDepassements(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.depassements ?? 0} label="relevés hors norme" /> },
      { titre: 'Permis de travail', fetcher: () => metierAPI.getQhsePermis(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.permis ?? 0} label="permis" /> },
      { titre: 'Formations QHSE', fetcher: () => metierAPI.getQhseFormations(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.expirees ?? d.total ?? 0} label="expirées" /> },
      { titre: 'Quasi-accidents', fetcher: () => metierAPI.getQhseQuasiAccidents(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.quasi ?? 0} label="enregistrés" /> },
      { titre: 'Chambre froide', fetcher: () => metierAPI.getFroidBilan('—').catch(() => ({ data: { note: 'Voir /metier/calculs' } })),
        render: () => <Link href="/metier/calculs" className="text-sm text-blue-600 hover:underline">Ouvrir l'analyse →</Link> },
    ],
  },
  {
    nom: 'Commercial & Clients',
    widgets: [
      { titre: 'Chiffre d’affaires', fetcher: () => metierAPI.getRentabilite(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.ca_ttc_xaf} label={`XAF TTC — ${nf(d.factures_total)} factures`} /> },
      { titre: 'Rentabilité missions', fetcher: () => metierAPI.getRentabiliteMissions(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.marge_totale_xaf} label={`XAF marge — ${nf(d.missions_total)} missions`} /> },
      { titre: 'Pipeline commercial', fetcher: () => metierAPI.getCommercialPipeline(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={(d.pipeline as Data)?.total ?? 0} label="opportunités" /> },
      { titre: 'Prestataires homologués', fetcher: () => metierAPI.getPrestatairesHomologues(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.homologues ?? 0} label="homologués" /> },
      { titre: 'Performance annuaire', fetcher: () => metierAPI.getAnnuairePerformance(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.note_moyenne ?? d.total ?? 0} label="note moyenne" /> },
      { titre: 'Docs prestataires expirés', fetcher: () => metierAPI.getAnnuaireDocsExpires(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.expires ?? 0} label="expirés" /> },
    ],
  },
  {
    nom: 'Support & Administration',
    widgets: [
      { titre: 'Tickets support', fetcher: () => metierAPI.getSupportStats(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.tickets ?? 0} label="tickets" /> },
      { titre: 'Maintenance tickets', fetcher: () => metierAPI.getMaintenanceTickets(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? Object.keys(d).length} label="par sévérité" /> },
      { titre: 'Collaborateurs', fetcher: () => metierAPI.getCollaborateursConformite(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.taux_conformite ?? d.total ?? 0} label="% conformité" /> },
      { titre: 'Frais à régulariser', fetcher: () => metierAPI.getFraisAvances(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.a_regulariser ?? d.total ?? 0} label="avances" /> },
      { titre: 'TVA récupérable', fetcher: () => metierAPI.getFraisTva(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.tva_attente_xaf} label={`XAF — ${nf(d.en_attente)} en attente`} /> },
      { titre: 'Scorecards', fetcher: () => metierAPI.getReportsScorecards(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? Object.keys(d).length} label="par pôle" /> },
      { titre: 'Accréditations', fetcher: () => metierAPI.getAccreditations(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.expirees ?? d.total ?? 0} label="expirées" /> },
      { titre: 'Quotas tenants', fetcher: () => metierAPI.getAdminQuotas(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.depassements ?? d.total ?? 0} label="dépassés" /> },
      { titre: 'Sauvegardes', fetcher: () => metierAPI.getAdminSauvegardes(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.sauvegardes ?? 0} label="tenants" /> },
      { titre: 'Abonnements', fetcher: () => metierAPI.getOrganisationAbonnements(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.expires_bientot ?? d.total ?? 0} label="expire bientôt" /> },
      { titre: 'Santé modules', fetcher: () => metierAPI.getDashboardSante(),
        render: (d) => {
          const m = d.modules as Data | undefined;
          return m && !isNote(m) ? <Big value={m.degradees} label={`dégradés / ${nf(m.modules_total)}`} /> : <Empty d={d} />;
        } },
      { titre: 'Incidents plateforme', fetcher: () => metierAPI.getSuperadminIncidents(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.ouverts ?? d.total ?? 0} label="ouverts" /> },
      { titre: 'Signalements chat', fetcher: () => metierAPI.getChatSignalements(),
        render: (d) => isNote(d) ? <Empty d={d} /> : <Big value={d.total ?? d.signalements ?? 0} label="en attente" /> },
    ],
  },
];

export default function MetierPage() {
  const [data, setData] = useState<Record<string, Data>>({});
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const all = SECTIONS.flatMap((s) => s.widgets);
    const results = await Promise.allSettled(
      all.map(async (w) => [w.titre, (await w.fetcher()).data] as const)
    );
    const next: Record<string, Data> = {};
    results.forEach((e) => {
      if (e.status === 'fulfilled') next[e.value[0]] = e.value[1];
    });
    setData(next);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="p-6 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Pilotage métier</h1>
          <p className="text-sm text-gray-500">
            {SECTIONS.reduce((n, s) => n + s.widgets.length, 0)} indicateurs — données réelles uniquement.
          </p>
        </div>
        <button onClick={load}
          className="flex items-center gap-2 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Actualiser
        </button>
      </div>

      {SECTIONS.map((s) => (
        <section key={s.nom}>
          <h2 className="text-lg font-semibold mb-3 border-b pb-2">{s.nom}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {s.widgets.map((w) => (
              <div key={w.titre} className="bg-white border rounded-xl p-5 shadow-sm">
                <p className="text-sm font-medium text-gray-700 mb-3">{w.titre}</p>
                {data[w.titre] ? w.render(data[w.titre]) : (
                  <p className="text-sm text-gray-400">{loading ? 'Chargement…' : 'Indisponible'}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
