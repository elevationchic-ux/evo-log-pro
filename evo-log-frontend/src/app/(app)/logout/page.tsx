'use client';

import React, { useEffect, useState } from 'react';
import { signOut } from 'next-auth/react';
import { LogOut, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function LogoutPage() {
  const [countdown, setCountdown] = useState(3);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          signOut({ callbackUrl: '/login' });
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="fixed inset-0 z-50 bg-slate-950 text-white flex items-center justify-center p-4 font-sans select-none">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-md w-full text-center shadow-2xl space-y-6 animate-in zoom-in-95 duration-300">
        <div className="w-16 h-16 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-amber-500/10">
          <LogOut className="w-8 h-8" />
        </div>

        <div>
          <h1 className="text-2xl font-black text-slate-100">Déconnexion Sécurisée</h1>
          <p className="text-sm text-slate-400 mt-1">Fermeture de session en cours. Vos données sont protégées.</p>
        </div>

        <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl flex items-center justify-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span className="text-xs text-slate-300 font-mono">Session nettoyée • Redirection dans <b className="text-amber-400 font-bold">{countdown}s</b></span>
        </div>

        <button
          onClick={() => signOut({ callbackUrl: '/login' })}
          className="w-full py-3 bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold rounded-xl text-sm shadow-lg shadow-amber-600/30 transition-all cursor-pointer"
        >
          Rediriger Maintenant
        </button>

        <div className="pt-4 border-t border-slate-800/80 flex items-center justify-center gap-1.5 text-xs text-slate-500 font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-amber-400" /> Code Axis Digital Cameroun (CADC)
        </div>
      </div>
    </div>
  );
}
