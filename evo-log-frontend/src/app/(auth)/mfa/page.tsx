'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

export const dynamic = 'force-dynamic';

export default function MfaPage() {
  const router = useRouter();

  const [code, setCode] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (code.length < 6) {
      toast.error('Veuillez saisir un code TOTP à 6 chiffres valide');
      return;
    }
    toast.success('Double authentification (MFA) validée !');
    router.push('/dashboard/global');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="w-12 h-12 bg-indigo-500/10 text-indigo-400 rounded-2xl flex items-center justify-center mb-6">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-black mb-2">Double Authentification (MFA)</h1>
        <p className="text-sm text-slate-400 mb-6">Saisissez le code de sécurité généré par votre application Authenticator.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Code TOTP (6 chiffres)</label>
            <input
              type="text"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
              placeholder="123456"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-center text-2xl font-mono tracking-widest text-indigo-400 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition-all"
          >
            Vérifier & Se Connecter <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
