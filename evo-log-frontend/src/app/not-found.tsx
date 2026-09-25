import Link from 'next/link';
import { Compass, LayoutDashboard, Ship, FileText, Truck, Package, Wallet, Keyboard } from 'lucide-react';

const QUICK_LINKS = [
  { href: '/acconage', label: 'Acconage & Magasinnage', icon: Ship },
  { href: '/transit', label: 'Transit & Douane', icon: FileText },
  { href: '/transport', label: 'Transport & Flotte', icon: Truck },
  { href: '/magasin', label: 'Magasin & Stocks', icon: Package },
  { href: '/finance', label: 'Finance & Comptabilité', icon: Wallet },
];

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-slate-100 px-4">
      <div className="max-w-lg w-full text-center space-y-6">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30">
          <Compass className="w-8 h-8 text-amber-400" />
        </div>

        <div>
          <h1 className="text-5xl font-black tracking-tight text-amber-400">404</h1>
          <p className="mt-3 text-lg font-semibold">Cette page n&apos;existe pas (ou plus)</p>
          <p className="mt-2 text-sm text-slate-400 leading-relaxed">
            Pas d&apos;inquiétude : rien n&apos;a été perdu. L&apos;adresse saisie ne correspond à
            aucun écran de EVO-LOG. Elle a peut-être été renommée, ou le lien était obsolète.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 text-slate-950 text-sm font-bold hover:bg-amber-400 transition-colors"
          >
            <LayoutDashboard className="w-4 h-4" />
            Retour au tableau de bord
          </Link>
          <div className="inline-flex items-center gap-2 text-xs text-slate-500">
            <Keyboard className="w-4 h-4" />
            Astuce : utilisez la recherche (T-Code) en haut de l&apos;écran pour trouver n&apos;importe quel module.
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800">
          <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">
            Modules les plus consultés
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2">
            {QUICK_LINKS.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:border-amber-500/40 hover:text-amber-300 transition-colors"
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
