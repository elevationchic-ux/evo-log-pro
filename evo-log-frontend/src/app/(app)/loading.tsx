/**
 * Squelette de chargement global du workspace : affiche des cartes videes
 * pendant la resolution du layout et des pages du groupe (app).
 */
export default function AppLoading() {
  return (
    <div className="p-4 sm:p-6 space-y-6 animate-pulse" aria-busy="true" aria-label="Chargement de la page">
      <div className="space-y-2">
        <div className="h-3 w-40 rounded bg-slate-800" />
        <div className="h-6 w-72 rounded bg-slate-800" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 rounded-2xl bg-slate-900 border border-slate-800" />
        ))}
      </div>
      <div className="h-64 rounded-2xl bg-slate-900 border border-slate-800" />
    </div>
  );
}
