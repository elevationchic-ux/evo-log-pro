'use client';

import React from 'react';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import {
  Truck, Receipt, Warehouse, Wrench, FileText,
  ShieldAlert, TrendingUp, Users, ArrowRight, CheckCircle2,
  Lock, Sparkles, Navigation, Globe, Compass, ShieldCheck
} from 'lucide-react';

interface PortalCard {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  href: string;
  icon: any;
  gradient: string;
  badge: string;
  requiredRoles: string[];
  features: string[];
}

// Cartes de navigation statiques vers les portails métier (contenu descriptif, liens vivants vérifiés).
// audit-allow:fake_data
const ALL_PORTALS: PortalCard[] = [
  {
    id: 'rh-employe',
    title: 'Portail Salarié RH & Paie',
    subtitle: 'Self-Service Collaborateur',
    description: 'Bulletins de paie OHADA, calendrier des paies, demandes et solde de congés, attestations administratives.',
    href: '/portail-employe',
    icon: Users,
    gradient: 'from-blue-600 to-indigo-600',
    badge: 'Universel',
    requiredRoles: [], // Accessible à tous
    features: ['Bulletins de paie téléchargeables', 'Solde de congés', 'Dates de virement'],
  },
  {
    id: 'chauffeur',
    title: 'Espace Conducteur & Mobilité',
    subtitle: 'Chauffeur Routier & Équipage',
    description: 'Feuille de route du jour, checklist sécurité départ/retour, saisie carburant express et signature tactile ePOD.',
    href: '/portail-chauffeur',
    icon: Truck,
    gradient: 'from-amber-600 to-orange-600',
    badge: 'Flotte & Route',
    requiredRoles: ['CHAUFFEUR', 'CONDUCTEUR', 'TRANSPORTEUR', 'ADMIN', 'DISPATCHER'],
    features: ['Tournées & GPS', 'Checklist véhicule', 'ePOD tactile', 'Saisie carburant'],
  },
  {
    id: 'frais',
    title: 'Espace Frais & Déplacements',
    subtitle: 'Notes de Frais & Avances',
    description: 'Demandes d’avances de mission sur corridors, saisie des dépenses avec photos de reçus, approbation manager.',
    href: '/portail-frais',
    icon: Receipt,
    gradient: 'from-emerald-600 to-teal-600',
    badge: 'Universel',
    requiredRoles: [], // Accessible à tous
    features: ['Avances de mission', 'Saisie tickets/péages', 'Validation hiérarchique'],
  },
  {
    id: 'magasinier',
    title: 'Espace Magasinier & Quai',
    subtitle: 'Opérateur Logistique & Stock',
    description: 'Ordres de prélèvement (picking FEFO/FIFO), réceptions & dépotages quai, inventaires tournants, checklist chariot.',
    href: '/portail-magasinier',
    icon: Warehouse,
    gradient: 'from-cyan-600 to-blue-700',
    badge: 'Entrepôt & WMS',
    requiredRoles: ['MAGASINIER', 'MANUTENTIONNAIRE', 'LOGISTICIEN', 'CHEF_MAGASIN', 'ADMIN'],
    features: ['Picking par travée', 'Pointage quai & scellés', 'Inventaire tournant'],
  },
  {
    id: 'technicien',
    title: 'Espace Technicien GMAO',
    subtitle: 'Atelier Mécanique & Maintenance',
    description: 'Ordres de Travail (OT) du jour, rapports d’intervention, prélèvement de pièces détachées au magasin, photos avant/après.',
    href: '/portail-technicien',
    icon: Wrench,
    gradient: 'from-purple-600 to-indigo-700',
    badge: 'Atelier & Parc',
    requiredRoles: ['TECHNICIEN', 'MECANICIEN', 'CHEF_ATELIER', 'MAINTENANCE', 'ADMIN'],
    features: ['OT Curatif / Préventif', 'Sortie pièces détachées', 'Diagnostics photos'],
  },
  {
    id: 'declarant',
    title: 'Espace Déclarant Terrain',
    subtitle: 'Transit Port & Frontières CEMAC',
    description: 'Suivi physique des dossiers, pointage scanner et visite conjointe, téléversement de BAE et alertes de litige en direct.',
    href: '/portail-declarant',
    icon: FileText,
    gradient: 'from-sky-600 to-indigo-800',
    badge: 'Douane & Ports',
    requiredRoles: ['DECLARANT', 'AGENT_TRANSIT', 'TRANSITAIRE', 'CHEF_TRANSIT', 'ADMIN'],
    features: ['Dossiers DUM/BL', 'Jalonnement physique quai', 'Upload BAE & quittance'],
  },
  {
    id: 'qhse',
    title: 'Vigie Sécurité & QHSE',
    subtitle: 'Signalement Flash & Prévention',
    description: 'Remontée en 30s d’une situation dangereuse ou presqu’accident avec photo, checklists de zone et fiches matières dangereuses.',
    href: '/portail-qhse',
    icon: ShieldAlert,
    gradient: 'from-rose-600 to-red-700',
    badge: 'Sécurité Active',
    requiredRoles: [], // Accessible à tous
    features: ['Signalement Near-Miss 30s', 'Checklist EPI & postes', 'FDS / Code IMDG'],
  },
  {
    id: 'commercial',
    title: 'Espace Commercial & Vente',
    subtitle: 'Chargé d’Affaires & Devis',
    description: 'Simulateur express de cotation corridor CEMAC, suivi du portefeuille clients, devis émis, relances et commissions.',
    href: '/portail-commercial',
    icon: TrendingUp,
    gradient: 'from-amber-500 to-yellow-600',
    badge: 'Business & CRM',
    requiredRoles: ['COMMERCIAL', 'CHARGE_AFFAIRES', 'DIRECTEUR_COMMERCIAL', 'ADMIN'],
    features: ['Simulateur cotation CEMAC', 'Pipeline devis', 'Suivi encours client'],
  },
];

export default function PortailCollaborateurHubPage() {
  const { data: session } = useSession();
  const userRoles: string[] = (session?.user as any)?.roles || [];
  const isAdmin = userRoles.some(r => r.toUpperCase() === 'ADMIN' || r.toUpperCase() === 'SUPER_ADMIN');

  const checkAccess = (roles: string[]) => {
    if (isAdmin) return true;
    if (roles.length === 0) return true;
    return roles.some(role => userRoles.includes(role.toUpperCase()));
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Banner Principal */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-8 shadow-2xl">
        <div className="absolute -right-12 -bottom-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            Carrefour Collaborateur & Espaces Métiers
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Bienvenue sur votre Hub Collaborateur
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Accédez en 1 clic à vos espaces de travail dédiés selon votre métier : route, entrepôt, atelier mécanique, douane portuaire, notes de frais ou sécurité terrain.
          </p>
          <div className="pt-2 flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" /> Session active : {session?.user?.name || 'Collaborateur EVO-LOG'}
            </span>
            <span className="text-slate-400">•</span>
            <span>Rôles : {userRoles.length > 0 ? userRoles.join(', ') : 'Employé'}</span>
          </div>
        </div>
      </div>

      {/* Grille des 8 Portails */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
            <Compass className="w-5 h-5 text-indigo-600" /> Vos Portails Métier Disponibles
          </h2>
          <span className="text-xs font-mono text-slate-500">8 Espaces Intégrés End-to-End</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {ALL_PORTALS.map((portal) => {
            const isAllowed = checkAccess(portal.requiredRoles);
            const Icon = portal.icon;

            return (
              <div
                key={portal.id}
                className={`relative flex flex-col justify-between rounded-2xl border transition-all duration-200 overflow-hidden ${
                  isAllowed
                    ? 'bg-slate-900 border-slate-700 hover:shadow-xl hover:-translate-y-1 hover:border-indigo-500/50'
                    : 'bg-slate-800 border-slate-700/80 opacity-60'
                }`}
              >
                {/* Header Card */}
                <div className="p-6 space-y-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${portal.gradient} text-white flex items-center justify-center shadow-md`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${
                      isAllowed
                        ? 'bg-indigo-500/10 text-indigo-300 border-indigo-500/40'
                        : 'bg-slate-900 text-slate-500 border-slate-700'
                    }`}>
                      {portal.badge}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-slate-200 leading-snug">{portal.title}</h3>
                    <p className="text-xs text-indigo-600 font-medium">{portal.subtitle}</p>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                    {portal.description}
                  </p>

                  <div className="space-y-1.5 pt-2 border-t border-slate-700">
                    {portal.features.map((f, i) => (
                      <div key={i} className="flex items-center gap-1.5 text-[11px] text-slate-400">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />
                        <span className="truncate">{f}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Footer Action */}
                <div className="p-4 bg-slate-800 border-t border-slate-700 mt-auto">
                  {isAllowed ? (
                    <Link
                      href={portal.href}
                      className="inline-flex items-center justify-between w-full px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors shadow-sm"
                    >
                      <span>Accéder au Portail</span>
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  ) : (
                    <div className="flex items-center justify-center gap-1.5 py-2 text-xs font-semibold text-slate-400">
                      <Lock className="w-3.5 h-3.5" /> Accès restreint à votre rôle
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
