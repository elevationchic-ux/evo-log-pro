/**
 * RBAC granulaire côté frontend.
 *
 * Reproduit fidèlement la sémantique du moteur backend
 * (`app/core/permissions.py`) pour que l'UI masque / affiche les actions
 * exactement comme l'API les autorise. Les codes suivent le format pointu
 * `module.sous_module.action` avec jokers segmentaires `*`.
 *
 * Non-régression : si la session ne porte AUCUNE permission granulaire
 * (tenant non "seedé"), `can()` retombe sur l'ancienne logique
 * `modules_allowed` / `requiredRoles`. Un tenant non migré garde donc le
 * comportement visuel d'aujourd'hui.
 */

export interface SessionUser {
  roles?: string[]
  permissions?: string[]
  shared_modules?: string[]
  modules_allowed?: string[]
  role_level?: number
  company_id?: number | null
  department_id?: number | null
  is_superuser?: boolean
}

const SEP = '.'

/** Le code accordé `granted` couvre-t-il le code requis `wanted` ? */
export function matchPermission(granted: string, wanted: string): boolean {
  if (granted === '*' || wanted === '*') return true
  const g = granted.split(SEP)
  const w = wanted.split(SEP)
  if (g.length < w.length) {
    g.push(...Array(w.length - g.length).fill('*'))
  }
  for (let i = 0; i < w.length; i++) {
    if (g[i] === '*') continue
    if (g[i] !== w[i]) return false
  }
  return true
}

export function hasPermission(user: SessionUser | undefined | null, code: string): boolean {
  if (!user) return false
  if (user.is_superuser) return true
  const level = user.role_level ?? 99
  // SuperAdmin (0) et Admin Entreprise (1) bypassent la granularité.
  if (level === 0 || level === 1) return true

  const moduleCode = (code || '').split(SEP)[0]

  // Module commun à toute l'entreprise : ouvert à tout utilisateur authentifié.
  const shared = (user.shared_modules || []).map((m) => String(m).toLowerCase())
  if (moduleCode && shared.includes(moduleCode.toLowerCase())) return true

  const codes = user.permissions || []
  if (codes.length > 0) {
    return codes.some((c) => matchPermission(c, code))
  }
  // Retro-compatibilité : aucun seed granulaire -> repli sur modules_allowed.
  const allowed = (user.modules_allowed || []).map((m) => String(m).toLowerCase())
  if (allowed.includes('all')) return true
  return moduleCode ? allowed.includes(moduleCode.toLowerCase()) : true
}

/** Vraie si l'utilisateur possède au moins une permission granulaire seedée. */
export function hasGranularPermissions(user: SessionUser | undefined | null): boolean {
  return !!user && Array.isArray(user.permissions) && user.permissions.length > 0
}
