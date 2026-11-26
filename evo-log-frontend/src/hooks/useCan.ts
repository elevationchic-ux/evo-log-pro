'use client'

import { useSession } from 'next-auth/react'
import { hasPermission, hasGranularPermissions, type SessionUser } from '@/lib/permissions'

/**
 * Hook de contrôle d'accès granulaire.
 *
 *   const can = useCan()
 *   if (can('comptabilite.journal.create')) { ... }
 *
 * Reproduit la décision de l'API. En l'absence de permissions granulaires
 * seedées (tenant non migré), retombe sur `modules_allowed` : comportement
 * identique à aujourd'hui.
 */
export function useCan(): (code: string) => boolean {
  const { data: session } = useSession()
  const user = session?.user as SessionUser | undefined
  return (code: string) => hasPermission(user, code)
}

/** Version booléenne immédiate pour un seul code. */
export function useCanCode(code: string): boolean {
  const { data: session } = useSession()
  const user = session?.user as SessionUser | undefined
  return hasPermission(user, code)
}

export { hasGranularPermissions }
