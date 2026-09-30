'use client';

import React from 'react';
import { Globe, PlugZap, FileWarning } from 'lucide-react';
import Link from 'next/link';

export default function TransitDouaneBae() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="bg-slate-900/90 border border-cyan-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-black tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
            Bulletins de Transit CEMAC
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
          <Globe className="w-8 h-8 text-cyan-400" />
          BAE — Transit Communautaire CEMAC
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Bulletins d&apos;Analyse et d&apos;Expédition (BAE), cautionnements, apurement et contentieux.
        </p>
      </div>

      {/* Honest unavailable state — no data source wired */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl shadow-xl p-10">
        <div className="max-w-xl mx-auto text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto">
            <PlugZap className="w-7 h-7 text-amber-400" />
          </div>
          <h2 className="text-lg font-black text-slate-100">Module non connecté</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Le suivi des BAE (titres de transit communautaire, cautionnements et apurement)
            n&apos;est pas encore adossé à une source de données réelle dans cette installation.
            Aucun enregistrement n&apos;est affiché pour ne pas induire de fausse information.
          </p>
          <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
            <FileWarning className="w-4 h-4" />
            Cette page n&apos;affiche volontairement aucune donnée fictive.
          </div>
          <div className="pt-2">
            <Link
              href="/transit-douane/dossiers-cemac"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-cyan-500 hover:to-teal-400 text-white font-black text-xs rounded-xl shadow-lg shadow-cyan-500/25 transition-all"
            >
              Consulter les dossiers de transit enregistrés
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
