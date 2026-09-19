'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldAlert, ArrowLeft, Lock } from 'lucide-react';

export default function RegisterPage() {
  return (
    <div className="fixed inset-0 z-50 bg-slate-950 text-white flex items-center justify-center p-4 font-sans select-none overflow-hidden">
      <div className="relative z-10 bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-md w-full text-center shadow-2xl space-y-6 animate-in zoom-in-95 duration-300">
        <div className="w-16 h-16 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-amber-500/10">
          <Lock className="w-8 h-8" />
        </div>

        <div>
          <span className="text-xs font-black tracking-widest text-amber-400 uppercase bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20 mb-2 inline-block">
            Politique de Sécurité CADC
          </span>
          <h1 className="text-2xl font-black text-slate-100 mt-1">Création de Compte Restreinte</h1>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            La création autonome de compte est désactivée sur cet ERP. Seul un **administrateur autorisé** peut créer un profil utilisateur et attribuer les rôles et permissions associés.
          </p>
        </div>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl flex items-center gap-3 text-left">
          <ShieldAlert className="w-6 h-6 text-amber-400 shrink-0" />
          <p className="text-xs text-slate-300">
            Veuillez vous rapprocher de la Direction des Systèmes d'Information (DSI CADC) pour demander l'ouverture de votre compte.
          </p>
        </div>

        <Link
          href="/login"
          className="w-full py-3.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-black rounded-xl text-sm shadow-xl shadow-amber-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Retour à la Page de Connexion
        </Link>

        <p className="text-[11px] text-slate-500 font-mono">
          © 2026 Code Axis Digital Cameroun (CADC)
        </p>
      </div>
    </div>
  );
}
