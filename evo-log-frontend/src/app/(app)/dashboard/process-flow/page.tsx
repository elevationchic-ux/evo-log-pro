'use client';

/**
 * Processus Navire → Client : vue pédagogique du pipeline end-to-end de l'ERP.
 * Chaque étape renvoie vers l'écran réel où le processus se déroule.
 * Aucune donnée chiffrée n'est affichée : les compteurs temps réel vivent dans
 * les modules concernés (le backend ne publie pas d'agrégat pipeline global).
 * audit-allow:fake_data  le tableau ETAPES est du contenu de navigation
 * descriptif (libellés + liens), pas des données d'exécution simulées.
 */
import React from 'react';
import Link from 'next/link';
import {
  Ship, ScrollText, Landmark, Forklift,
  Truck, PackageCheck, FileSignature, ChevronRight, BookOpen,
} from 'lucide-react';
import { ModuleLayout } from '@/components/layout/ModuleLayout';

interface EtapeProcessus {
  num: number;
  titre: string;
  icone: typeof Ship;
  couleur: string;
  resume: string;       // ce qui se passe à cette étape (pédagogie novice)
  ecran: { label: string; href: string };  // écran réel de l'ERP
  tcode?: string;
}

const ETAPES: EtapeProcessus[] = [
  {
    num: 1,
    titre: 'Arrivée du navire & consignment',
    icone: Ship,
    couleur: 'text-sky-400 border-sky-500/30 bg-sky-500/10',
    resume: "Le navire est enregistré dans la place : dossier de consignment, ETA, plan d'arrimage.",
    ecran: { label: "Opérations navire", href: '/port-operations/vessel-consignment' },
  },
  {
    num: 2,
    titre: 'Manifeste & Bill of Lading',
    icone: ScrollText,
    couleur: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
    resume: 'Les chargements déclarés au manifeste sont rapprochés des BL pour identifier chaque container.',
    ecran: { label: 'Manifestes', href: '/port-operations/manifests' },
  },
  {
    num: 3,
    titre: 'Dédouanement (CAMCIS / GUCE)',
    icone: Landmark,
    couleur: 'text-violet-400 border-violet-500/30 bg-violet-500/10',
    resume: "Déclarations en douane DUM, taxation CEMAC, apurement des titres de transit jusqu'à la mainlevée.",
    ecran: { label: 'Déclarations douanières', href: '/transit-douane/declarations' },
  },
  {
    num: 4,
    titre: 'Acconage & sortie de quai',
    icone: Forklift,
    couleur: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
    resume: "Manutention portuaire : pesée VGM, constat d'avarie éventuel, enlèvement du container hors du quai.",
    ecran: { label: 'Opérations de quai', href: '/port-operations/quai-operations' },
  },
  {
    num: 5,
    titre: 'Enlèvement & passage en magasin',
    icone: PackageCheck,
    couleur: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    resume: 'La marchandise est réceptionnée en entrepôt (réception MAG3) ou remise directement au client.',
    ecran: { label: 'Réception magasin', href: '/magasin/reception-mag3' },
  },
  {
    num: 6,
    titre: 'Transport & livraison client',
    icone: Truck,
    couleur: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10',
    resume: "Mission de transport créée, suivi GPS du véhicule, e-POD signé à la livraison.",
    ecran: { label: 'Missions de transport', href: '/transport/missions' },
  },
  {
    num: 7,
    titre: 'Facturation & recouvrement',
    icone: FileSignature,
    couleur: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
    resume: 'Facturation des débours et prestations, suivi des encaissements, litiges clients.',
    ecran: { label: 'Facturation', href: '/finance/invoicing' },
  },
];

export default function ProcessFlowPage() {
  return (
    <ModuleLayout
      title="Processus Navire → Client"
      description="Le parcours complet d'une marchandise importée, du déchargement du navire jusqu'à la facture payée. Chaque étape cliquable ouvre l'écran où le travail réel s'effectue."
      help="Cette page est une carte d'orientation : elle explique l'ordre logique des modules de l'ERP. Pour suivre les dossiers en cours, utilisez plutôt les tableaux de bord de chaque module."
    >
      <div className="space-y-3">
        {ETAPES.map((etape, idx) => {
          const Icone = etape.icone;
          return (
            <div key={etape.num} className="relative">
              {/* Connecteur vertical entre étapes */}
              {idx < ETAPES.length - 1 && (
                <div className="absolute left-[27px] top-[58px] bottom-[-14px] w-px bg-slate-800" aria-hidden />
              )}
              <div className="flex items-stretch gap-3 sm:gap-4">
                <div className={`shrink-0 w-14 h-14 rounded-2xl border flex flex-col items-center justify-center font-black text-sm ${etape.couleur}`}>
                  <span className="text-[10px] opacity-70 leading-none">ÉT</span>
                  {etape.num}
                </div>
                <div className="flex-1 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center gap-3 hover:border-slate-700 transition-colors">
                  <div className="min-w-0 flex-1">
                    <h3 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
                      <Icone className="w-4 h-4 shrink-0 text-slate-400" />
                      {etape.titre}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">{etape.resume}</p>
                  </div>
                  <Link
                    href={etape.ecran.href}
                    className="shrink-0 inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-bold text-amber-400 hover:bg-slate-700 hover:text-amber-300 transition-colors min-h-11"
                  >
                    <span className="hidden sm:inline">{etape.ecran.label}</span>
                    <span className="sm:hidden">Ouvrir</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-start gap-3 rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-xs text-slate-400">
        <BookOpen className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
        <p>
          Les compteurs temps réel (dossiers en cours, containers au quai, missions actives) sont consultables
          dans le <Link href="/dashboard" className="text-amber-400 font-semibold hover:underline">tableau de bord global</Link>  cette vue de processus n&apos;affiche volontairement aucun chiffre simulé.
        </p>
      </div>
    </ModuleLayout>
  );
}
