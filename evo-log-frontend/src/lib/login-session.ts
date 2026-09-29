// src/lib/login-session.ts  Ouverture de session NextAuth depuis un jalon
// backend deja valide.
//
// Le formulaire de connexion et l'ecran 2FA appellent tous deux /api/v1/auth/*
// elles-mêmes (le backend décide seul du mot de passe, du TOTP et des codes de
// secours). Ce qui reste au front est la deuxieme moitie : transformer l'
// « access_token » obtenu en vraie session NextAuth, puis recuperer les roles
// reels pour choisir la page d'atterrissage. Centralise ici pour que les deux
// chemins partagent exactement la meme logique (et le meme setCookie).
import { getSession, signIn } from 'next-auth/react'

export interface LoginOutcome {
  ok: boolean
  /** Roles effectifs renvoyes par le backend ; vide si la session a echoue. */
  roles: string[]
  /** Le backend impose un changement de mot de passe a la premiere connexion. */
  mustChangePassword: boolean
  /** Message lisible, toujours dans la langue du chrome (FR par defaut). */
  message?: string
}

/**
 * Ouvre une session NextAuth a partir d'un access token backend deja emis.
 * `authorize` ne renvoie jamais le mot de passe : il revalide le jalon via
 * GET /api/v1/auth/session, ce qui evite un second /login (et son compteur de
 * tentatives) pour une seule connexion utilisateur.
 */
export async function establishSession(ticket: string): Promise<LoginOutcome> {
  if (!ticket) {
    return { ok: false, roles: [], mustChangePassword: false, message: 'Aucun jeton de session recu.' }
  }
  const res = await signIn('credentials', { ticket, redirect: false })
  if (res?.error) {
    // next-auth ne remonte qu'un code d'erreur générique : on traduit côté front.
    return {
      ok: false,
      roles: [],
      mustChangePassword: false,
      message: "La session n'a pas pu etre ouverte. Relancez la connexion.",
    }
  }
  const session = await getSession()
  const user = (session?.user || {}) as Record<string, unknown>
  const roles = Array.isArray(user.roles) ? (user.roles as string[]) : []
  return {
    ok: !!session?.user,
    roles,
    mustChangePassword: !!user.must_change_password,
  }
}

/** Extrait les roles de la session courante (atterrissage apres un reload). */
export async function currentRoles(): Promise<string[]> {
  const session = await getSession()
  const user = (session?.user || {}) as Record<string, unknown>
  return Array.isArray(user.roles) ? (user.roles as string[]) : []
}
