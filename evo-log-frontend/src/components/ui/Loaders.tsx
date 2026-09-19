import React from 'react';

/**
 * FullScreenLoader: Écran de chargement ultra-pro & élégant CADC EM-ERP
 * Utilisé après la connexion et lors des transitions de routes principales
 */
export const FullScreenLoader = () => {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-between bg-slate-950 text-white z-50 p-6 sm:p-12 font-sans select-none overflow-hidden animate-in fade-in duration-300">
      {/* Dynamic Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-tr from-amber-500/15 via-yellow-500/10 to-amber-600/5 rounded-full blur-[140px] pointer-events-none animate-pulse" />

      {/* Top Header Badge */}
      <div className="z-10 pt-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 border border-amber-500/30 text-amber-300 text-xs font-bold uppercase tracking-wider backdrop-blur-md shadow-xl">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
          Code Axis Digital Cameroun (CADC)
        </div>
      </div>

      {/* Central Hero Loader */}
      <div className="z-10 flex flex-col items-center text-center my-auto max-w-md">
        <div className="relative flex items-center justify-center mb-6">
          <div className="absolute w-28 h-28 bg-amber-500/20 rounded-full animate-ping" style={{ animationDuration: '2.5s' }} />
          <div className="absolute w-20 h-20 bg-amber-500/30 rounded-full animate-pulse" />
          
          <div className="relative z-10 w-16 h-16 bg-gradient-to-tr from-amber-500 via-yellow-400 to-amber-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-amber-500/30 border border-amber-300/40">
            <span className="material-symbols-outlined text-slate-950 text-3xl animate-spin" style={{ animationDuration: '3s' }}>
              sync
            </span>
          </div>
        </div>

        <h1 className="text-3xl font-black bg-gradient-to-r from-amber-100 via-amber-300 to-amber-500 bg-clip-text text-transparent tracking-tight mb-2">
          EVO-LOG SaaS
        </h1>
        <p className="text-xs font-bold text-amber-400 uppercase tracking-widest animate-pulse">
          Chargement du Profil & Sécurisation de Session...
        </p>

        {/* High-tech Progress Bar */}
        <div className="w-full mt-6 bg-slate-900 border border-slate-800 p-1.5 rounded-full overflow-hidden shadow-inner">
          <div className="h-2 bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-300 rounded-full animate-pulse w-3/4 shadow-[0_0_10px_#f59e0b]" />
        </div>
      </div>

      {/* Footer */}
      <div className="z-10 pb-4 text-center text-xs text-slate-500 font-mono">
        Portail Entreprise Certifié • CADC 2026
      </div>
    </div>
  );
};

/**
 * CardSkeletonLoader: Chargeur de cartes pour tableaux de bord et formulaires
 */
export const CardSkeletonLoader = ({ className = '' }: { className?: string }) => {
  return (
    <div className={`w-full animate-pulse bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl ${className}`}>
      <div className="flex items-center gap-4 mb-4">
        <div className="w-12 h-12 bg-slate-800 rounded-xl shrink-0" />
        <div className="space-y-2 flex-1">
          <div className="h-4 bg-slate-800 rounded w-1/3" />
          <div className="h-3 bg-slate-800/60 rounded w-1/4" />
        </div>
      </div>
      <div className="space-y-3">
        <div className="h-3 bg-slate-800/70 rounded w-full" />
        <div className="h-3 bg-slate-800/70 rounded w-5/6" />
        <div className="h-3 bg-slate-800/70 rounded w-4/6" />
      </div>
    </div>
  );
};

export const TableSkeletonLoader = ({ columns = 5, rows = 6 }: { columns?: number, rows?: number }) => {
  return (
    <div className="w-full animate-pulse bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden">
      <div className="flex border-b border-slate-800 bg-slate-950 p-4">
        {Array.from({ length: columns }).map((_, i) => (
          <div key={`head-${i}`} className={`h-4 bg-slate-800 rounded ${i === 0 ? 'w-1/4' : 'w-1/6'} mr-4`} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={`row-${rowIndex}`} className="flex border-b border-slate-800/60 p-4 items-center">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <div 
              key={`cell-${rowIndex}-${colIndex}`} 
              className={`h-3 bg-slate-800/70 rounded ${colIndex === 0 ? 'w-1/3' : 'w-1/5'} mr-4`}
            />
          ))}
        </div>
      ))}
    </div>
  );
};
