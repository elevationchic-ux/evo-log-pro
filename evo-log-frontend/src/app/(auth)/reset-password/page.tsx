'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { KeyRound, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

export const dynamic = 'force-dynamic';

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Un lien de réinitialisation a été envoyé si l'adresse email existe.");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="w-12 h-12 bg-amber-500/10 text-amber-400 rounded-2xl flex items-center justify-center mb-6">
          <KeyRound className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-black mb-2">Réinitialisation de Mot de Passe</h1>
        <p className="text-sm text-slate-400 mb-6">Saisissez votre email professionnel pour recevoir les instructions.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Adresse Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="votre.email@entreprise.com"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3.5 bg-amber-600 hover:bg-amber-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-amber-600/30 transition-all"
          >
            Envoyer les Instructions <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-400">
          <Link href="/login" className="text-amber-400 font-bold hover:underline">Retour à la connexion</Link>
        </div>
      </div>
    </div>
  );
}
