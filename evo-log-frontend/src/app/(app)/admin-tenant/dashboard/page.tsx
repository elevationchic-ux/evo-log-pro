'use client';

import React, { useState } from 'react';
import {
  Shield, Users, Building2, Settings, Activity,
  Globe, Database, CheckCircle2, AlertTriangle, Plus
} from 'lucide-react';
import Link from 'next/link';

export default function AdminTenantDashboard() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-rose-500/30 p-6 rounded-3xl shadow-xl backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-wider uppercase bg-rose-500/20 text-rose-300 border border-rose-500/30">
              Console Super Administrateur CADC
            </span>
            <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              T-Code : KSUP_DSH
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-100 flex items-center gap-3">
            <Shield className="w-8 h-8 text-rose-400" />
            Administration Système & Multi-Tenant
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Gouvernance globale de la plateforme CADC ERP Logistique Portuaire, gestion des tenants, RBAC et audits.
          </p>
        </div>
      </div>

      {/* Métriques Système */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sociétés (Tenants) Actives</div>
          <div className="text-2xl font-black text-rose-400 font-mono">8</div>
          <div className="text-[11px] text-slate-400 mt-2">Cameroun, Tchad, RCA, Congo</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Utilisateurs Actifs</div>
          <div className="text-2xl font-black text-blue-400 font-mono">142</div>
          <div className="text-[11px] text-slate-400 mt-2">Tous rôles confondus</div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Disponibilité Système (SLA)</div>
          <div className="text-2xl font-black text-emerald-400 font-mono">99.94%</div>
          <div className="text-[11px] text-emerald-300/80 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Objectif 99.9% atteint
          </div>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Alertes Sécurité</div>
          <div className="text-2xl font-black text-amber-400 font-mono">1</div>
          <div className="text-[11px] text-amber-300/80 mt-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Tentative de connexion suspecte
          </div>
        </div>
      </div>

      {/* Modules Admin */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { href: '/admin-tenant/users-rbac', icon: Users, label: 'Gestion Utilisateurs & RBAC', desc: 'Création, rôles, permissions granulaires et accès T-Code par profil', tcode: 'KADM_USR' },
          { href: '/admin-tenant/multi-tenant', icon: Building2, label: 'Multi-Tenant & Sociétés', desc: 'Isolation des données, quotas de stockage et paramétrage par tenant', tcode: 'KSUP_ORG' },
          { href: '/admin-tenant/system-admin', icon: Settings, label: 'Administration Système', desc: 'Configuration globale CADC, paramètres réseau, journalisation, sauvegardes', tcode: 'KSUP_TNT' },
          { href: '/admin-tenant/audit-logs', icon: Activity, label: 'Journaux d Audit', desc: 'Traçabilité des actions utilisateurs, modifications critiques et connexions', tcode: 'KSUP_AUD' },
          { href: '/admin-tenant/integrations', icon: Globe, label: 'Intégrations & APIs', desc: 'Connecteurs Sage, Mobile Money (OM/MOMO), SYDONIA, GPS télémat.', tcode: 'KSUP_INT' },
          { href: '/admin-tenant/global-settings', icon: Database, label: 'Paramètres Globaux ERP', desc: 'Exercices comptables, devises, TVA, calendriers OHADA, référentiels', tcode: 'KSUP_CFG' },
        ].map(item => (
          <Link
            key={item.href}
            href={item.href}
            className="p-5 bg-slate-900/90 border border-slate-800 hover:border-rose-500/50 rounded-2xl transition-all group"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="p-3 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
                <item.icon className="w-6 h-6" />
              </div>
              <span className="font-mono text-xs text-amber-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                {item.tcode}
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-100 group-hover:text-rose-400 transition-colors">{item.label}</h3>
            <p className="text-xs text-slate-400 mt-1">{item.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
