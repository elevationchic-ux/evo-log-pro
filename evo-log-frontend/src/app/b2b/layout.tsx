'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Ship,
  Compass,
  Package,
  FileText,
  CreditCard,
  AlertCircle,
  Calculator,
  Globe,
  Bell,
  LogOut,
  Building2,
  ShieldCheck,
  Headphones,
  Search,
  CheckCircle2,
  Menu,
  X
} from 'lucide-react';
import { Toaster } from 'sonner';

export default function B2BPortalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [activeCompany, setActiveCompany] = useState({
    id: 1,
    name: 'CADC Logistics Cameroun',
    logo: '⚓',
    code: 'CADC-DLA',
    hotline: '+237 233 42 00 00',
    email: 'support-client@cadc-logistics.cm'
  });

  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(3);

  const navigationItems = [
    { label: 'Tableau de Bord', href: '/b2b/dashboard', icon: Compass },
    { label: 'Suivi Cargaisons & B/L', href: '/b2b/tracking', icon: Package },
    { label: 'Demande de Cotation', href: '/b2b/cotations', icon: Calculator },
    { label: 'Coffre-fort Documents', href: '/b2b/documents', icon: FileText },
    { label: 'Factures & Paiements', href: '/b2b/factures', icon: CreditCard },
    { label: 'Réclamations & Litiges', href: '/b2b/incidents', icon: AlertCircle },
  ];

  const isAuthPage = pathname === '/b2b' || pathname === '/b2b/login';

  if (isAuthPage) {
    return <div className="min-h-screen bg-slate-950 text-slate-100">{children}</div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-amber-500 selection:text-slate-950">
      <Toaster position="top-right" richColors />

      {/* Top Banner: Customer Portal Scope & Support */}
      <div className="bg-gradient-to-r from-amber-600 via-amber-500 to-yellow-500 text-slate-950 px-4 py-1.5 text-xs font-semibold flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4" />
          <span>Portail B2B Chargeurs & Importateurs Certifié • Espace Sécurisé Conforme CEMAC</span>
        </div>
        <div className="hidden md:flex items-center gap-4 text-[11px] font-mono">
          <span className="flex items-center gap-1"><Headphones className="w-3.5 h-3.5" /> Support 24/7 : {activeCompany.hotline}</span>
          <span>•</span>
          <span className="bg-slate-950/10 px-2 py-0.5 rounded font-bold">{activeCompany.name} ({activeCompany.code})</span>
        </div>
      </div>

      {/* Main Navigation Header */}
      <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-xl border-b border-slate-800 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Brand Logo & Portal Name */}
            <div className="flex items-center gap-3">
              <Link href="/b2b/dashboard" className="flex items-center gap-2.5 group">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-400 text-slate-950 font-black flex items-center justify-center text-xl shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform">
                  {activeCompany.logo}
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-black text-lg tracking-tight text-white">{activeCompany.name}</span>
                    <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">PORTAIL B2B</span>
                  </div>
                  <p className="text-[11px] text-slate-400">Guichet Client & Suivi Logistique Portuaire</p>
                </div>
              </Link>
            </div>

            {/* Quick Live Search bar (BL / Container) */}
            <div className="hidden lg:flex items-center flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Recherche directe : N° B/L (ex: CADC-BL-982) ou Conteneur (ex: MSKU729104)..."
                  className="w-full h-9 pl-9 pr-4 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 font-mono transition-all"
                />
              </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-3">
              {/* Currency Selector */}
              <div className="hidden sm:flex items-center gap-1 bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-xs text-slate-300 font-mono">
                <Globe className="w-3.5 h-3.5 text-amber-400" />
                <span className="font-bold text-amber-300">XAF (FCFA)</span>
              </div>

              {/* Notifications */}
              <Link href="/b2b/dashboard" className="relative p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-colors">
                <Bell className="w-4 h-4" />
                {unreadNotifications > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-slate-950 text-[10px] font-black flex items-center justify-center">
                    {unreadNotifications}
                  </span>
                )}
              </Link>

              {/* User / Client Profile Badge */}
              <div className="hidden sm:flex items-center gap-2.5 pl-2 border-l border-slate-800">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-500/20 to-yellow-500/20 border border-amber-500/40 text-amber-300 font-bold flex items-center justify-center text-xs">
                  SC
                </div>
                <div className="text-left">
                  <div className="text-xs font-bold text-slate-200">Société Camerounaise d'Import (SOCAM)</div>
                  <div className="text-[10px] text-slate-400 font-mono">Compte Chargeur #CLI-2026-88</div>
                </div>
              </div>

              {/* Logout Button */}
              <Link
                href="/b2b"
                className="p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 hover:text-red-400 hover:border-red-500/30 transition-colors"
                title="Quitter le portail B2B"
              >
                <LogOut className="w-4 h-4" />
              </Link>

              {/* Mobile menu trigger */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Desktop Sub-navigation tabs */}
          <nav className="hidden md:flex space-x-1 border-t border-slate-800/60 pt-1 pb-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-800 bg-slate-900 px-4 py-3 space-y-2 animate-in slide-in-from-top-2 duration-200">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-semibold ${
                    isActive ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30' : 'text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4 text-amber-400" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        )}
      </header>

      {/* Portal Main Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-slate-400 font-medium">Système Connecté en Direct aux Port de Douala (PAD) & Kribi (PAK)</span>
          </div>
          <div className="font-mono text-[11px] text-slate-500">
            © 2026 {activeCompany.name} • Propulsé par EVO-LOG SaaS Engine • Zone CEMAC
          </div>
        </div>
      </footer>
    </div>
  );
}
