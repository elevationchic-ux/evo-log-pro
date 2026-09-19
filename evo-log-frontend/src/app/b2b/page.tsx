'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Ship,
  Search,
  Lock,
  Mail,
  Building2,
  ArrowRight,
  ShieldCheck,
  Package,
  Globe2,
  Compass,
  FileCheck2,
  Headphones,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';

export default function B2BLandingPage() {
  const router = useRouter();

  // Instant public tracking state
  const [trackingNumber, setTrackingNumber] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Client login state
  const [companyCode, setCompanyCode] = useState('CADC-DLA');
  const [clientEmail, setClientEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const availableCompanies = [
    { code: 'CADC-DLA', name: 'CADC Logistics Cameroun (Port Douala/Kribi)', icon: '⚓' },
    { code: 'TCL-CEMAC', name: 'Trans-Cameroon Logistics (Corridors Tchad/RCA)', icon: '🚛' },
    { code: 'PAK-TERMINAL', name: 'Kribi Container Terminal Partner', icon: '🚢' },
    { code: 'CEMAC-FREIGHT', name: 'Central Africa Freight Forwarders', icon: '🌐' },
  ];

  const handleQuickTrack = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackingNumber.trim()) {
      toast.error('Veuillez saisir un numéro de B/L ou de Conteneur valide');
      return;
    }
    setIsSearching(true);
    setTimeout(() => {
      setIsSearching(false);
      router.push(`/b2b/tracking?query=${encodeURIComponent(trackingNumber.trim())}`);
    }, 400);
  };

  const handleClientLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientEmail || !password) {
      toast.error('Veuillez renseigner votre email et mot de passe');
      return;
    }

    setIsLoggingIn(true);
    setTimeout(() => {
      setIsLoggingIn(false);
      toast.success('Connexion réussie au portail chargeur !');
      router.push('/b2b/dashboard');
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-amber-500 selection:text-slate-950">
      
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 to-yellow-400 text-slate-950 font-black flex items-center justify-center text-2xl shadow-xl shadow-amber-500/20">
              ⚓
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-black tracking-tight text-white">PORTAIL B2B CHARGEURS</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">STANDALONE SaaS</span>
              </div>
              <p className="text-xs text-slate-400">Guichet Unique Client Logistique Portuaire & Transit CEMAC</p>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-4 text-xs font-mono">
            <span className="flex items-center gap-1.5 text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> Plateforme Sécurisée ISO/ISPS
            </span>
          </div>
        </div>
      </header>

      {/* Main Hero & Portals */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Column: Hero & Instant Tracking without Login */}
          <div className="lg:col-span-7 space-y-8">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold tracking-wide mb-4">
                <Sparkles className="w-3.5 h-3.5" /> Accès Direct aux Opérations Maritimes & Terrestres
              </div>
              <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white leading-tight">
                Suivez et gérez vos conteneurs en <span className="bg-gradient-to-r from-amber-400 via-yellow-300 to-amber-500 bg-clip-text text-transparent">temps réel</span>
              </h1>
              <p className="mt-3 text-sm text-slate-400 max-w-xl leading-relaxed">
                Accédez à l'état d'avancement de vos escales, documents douaniers (BAE, DUM), factures, et position de vos camions sur les corridors Douala - Yaoundé - N'Djamena - Bangui.
              </p>
            </div>

            {/* Public Live Tracking Box */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-sm font-bold text-slate-200">
                  <Package className="w-4 h-4 text-amber-400" /> Suivi Rapide Public (Sans Connexion)
                </div>
                <span className="text-[11px] font-mono text-slate-500">B/L • Conteneur • N° Booking</span>
              </div>

              <form onSubmit={handleQuickTrack} className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={trackingNumber}
                    onChange={(e) => setTrackingNumber(e.target.value)}
                    placeholder="Ex: CADC-BL-2026-908 ou MSKU8472910"
                    className="w-full h-12 pl-11 pr-4 bg-slate-950 border border-slate-700/80 rounded-2xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 font-mono"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSearching}
                  className="h-12 px-6 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-slate-950 font-black text-sm rounded-2xl flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition-all shrink-0 active:scale-95 disabled:opacity-70"
                >
                  {isSearching ? 'Recherche...' : <><span>Tracer le Fret</span><ArrowRight className="w-4 h-4" /></>}
                </button>
              </form>

              <div className="mt-4 flex flex-wrap items-center gap-2 text-[11px] text-slate-400 font-mono">
                <span className="text-slate-500">Exemples rapides :</span>
                <button
                  type="button"
                  onClick={() => setTrackingNumber('CADC-BL-2026-880')}
                  className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  CADC-BL-2026-880
                </button>
                <button
                  type="button"
                  onClick={() => setTrackingNumber('MSKU7829104')}
                  className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  MSKU7829104 (Douala-N'Djamena)
                </button>
              </div>
            </div>

            {/* Value Props Badges */}
            <div className="grid grid-cols-3 gap-4 pt-2">
              <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-3.5">
                <div className="text-amber-400 font-black text-lg">100%</div>
                <div className="text-xs text-slate-400 mt-0.5">Dédouanement Digitalisé (GUCE / SYDONIA)</div>
              </div>
              <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-3.5">
                <div className="text-amber-400 font-black text-lg">Live GPS</div>
                <div className="text-xs text-slate-400 mt-0.5">Corridors CEMAC Tchad & Centrafrique</div>
              </div>
              <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-3.5">
                <div className="text-amber-400 font-black text-lg">Instant e-POD</div>
                <div className="text-xs text-slate-400 mt-0.5">Preuve de Livraison avec signature tactile</div>
              </div>
            </div>
          </div>

          {/* Right Column: Independent Client Login Box */}
          <div className="lg:col-span-5">
            <div className="bg-slate-900/95 border border-slate-800 rounded-3xl p-8 shadow-2xl backdrop-blur-2xl relative">
              <div className="mb-6">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase mb-2">
                  <Lock className="w-3.5 h-3.5" /> Espace Sécurisé Client
                </div>
                <h2 className="text-2xl font-black text-white">Connexion Chargeur & Partenaire</h2>
                <p className="text-xs text-slate-400 mt-1">Accédez à votre espace facturation, cotations et documents certifiés.</p>
              </div>

              <form onSubmit={handleClientLogin} className="space-y-4">
                
                {/* Company / Enterprise Target Selector */}
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Prestataire Logistique Partenaire
                  </label>
                  <div className="relative">
                    <Building2 className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <select
                      value={companyCode}
                      onChange={(e) => setCompanyCode(e.target.value)}
                      className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 appearance-none font-medium"
                    >
                      {availableCompanies.map((c) => (
                        <option key={c.code} value={c.code} className="bg-slate-900 text-white">
                          {c.icon} {c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Email / Client ID */}
                <div>
                  <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Email ou Identifiant Client
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="email"
                      value={clientEmail}
                      onChange={(e) => setClientEmail(e.target.value)}
                      placeholder="client@socam-import.cm"
                      required
                      className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Mot de Passe
                    </label>
                    <span className="text-[11px] text-amber-400 hover:underline cursor-pointer">
                      Oublié ?
                    </span>
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      required
                      className="w-full h-11 pl-10 pr-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoggingIn}
                  className="w-full h-12 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-400 hover:to-yellow-300 text-slate-950 font-black text-sm rounded-xl flex items-center justify-center gap-2 shadow-xl shadow-amber-500/20 transition-all active:scale-[0.98] disabled:opacity-70 mt-2"
                >
                  {isLoggingIn ? 'Accès en cours...' : <><span>Ouvrir Mon Espace Client</span><ArrowRight className="w-4 h-4" /></>}
                </button>
              </form>

              <div className="mt-6 pt-4 border-t border-slate-800 text-center text-xs text-slate-400">
                <span>Vous êtes un nouvel importateur / chargeur ?</span>{' '}
                <button
                  onClick={() => router.push('/b2b/cotations')}
                  className="text-amber-400 hover:underline font-bold"
                >
                  Demander un compte ou une cotation
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Bottom Features Bar */}
      <footer className="border-t border-slate-800 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-6 text-slate-400">
            <span className="flex items-center gap-1.5"><Globe2 className="w-4 h-4 text-amber-400" /> Port de Douala (PAD)</span>
            <span className="flex items-center gap-1.5"><Ship className="w-4 h-4 text-cyan-400" /> Port en Eau Profonde de Kribi (PAK)</span>
            <span className="flex items-center gap-1.5"><Compass className="w-4 h-4 text-emerald-400" /> Corridors CEMAC</span>
          </div>
          <div className="font-mono text-[11px]">
            Portail B2B Indépendant • Accès Client Haute Sécurité
          </div>
        </div>
      </footer>
    </div>
  );
}
