'use client'

import { AlertTriangle } from 'lucide-react'

interface PageNonConnecteeProps {
  /** Nom de l'écran, affiché dans le bandeau */
  module?: string
  /** Message personnalisé optionnel */
  message?: string
}

/**
 * Bandeau d'honnêteté produit : affiche clairement qu'un écran n'est pas
 * (ou partiellement) branché sur les données réelles de la base.
 * À poser en tête de toute page encore statique ou basée sur des maquettes.
 */
export default function PageNonConnectee({ module, message }: PageNonConnecteeProps) {
  return (
    <div
      role="status"
      className="flex items-start gap-3 bg-amber-500/10 border border-amber-500/40 rounded-2xl px-4 py-3 mb-4"
    >
      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
      <div className="text-xs text-amber-200 leading-relaxed">
        <span className="font-black uppercase tracking-wider text-amber-400">
          Données non connectées
        </span>
        <span className="font-bold text-amber-300">{module ? ` • ${module}` : ''}</span>
        <p className="text-amber-200/90 mt-0.5">
          {message
            ?? 'Cet écran affiche des maquettes : il n\u2019est pas encore branché sur les données réelles de votre organisation. Les chiffres présentés ne doivent pas être utilisés pour décider.'}
        </p>
      </div>
    </div>
  )
}
