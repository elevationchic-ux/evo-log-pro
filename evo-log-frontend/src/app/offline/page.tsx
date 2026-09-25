import type { Metadata } from 'next'

/**
 * Page servie par le service worker (`public/sw.js`) quand la navigation
 * echoue hors connexion. Volontairement autonome : aucune donnee inventee,
 * aucun appel API (le reseau est justement cassé).
 */
export const metadata: Metadata = {
  title: 'Hors connexion',
  robots: { index: false, follow: false },
};

export default function OfflinePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-900 px-6 text-center text-slate-100">
      <span aria-hidden className="material-symbols-outlined text-6xl text-slate-400">
        cloud_off
      </span>
      <h1 className="text-2xl font-semibold">Vous êtes hors connexion</h1>
      <p className="max-w-md text-sm text-slate-300">
        Le réseau est indisponible. Les opérations enregistrées sur ce poste
        (tickets carburant, signatures ePOD, signalements) sont conservées et
        seront synchronisées automatiquement dès le retour de la connexion.
      </p>
      <div className="mt-2 flex gap-3">
        <a
          href="/"
          className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-500"
        >
          Réessayer
        </a>
        <a
          href="/transport/missions"
          className="rounded-xl border border-slate-600 px-5 py-2.5 text-sm font-medium text-slate-200 hover:bg-slate-800"
        >
          Voir mes missions
        </a>
      </div>
    </main>
  );
}
