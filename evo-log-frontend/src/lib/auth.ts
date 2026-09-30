/**
 * NextAuth v4 configuration for EVO-LOG frontend
 * Synchronized with backend RBAC system
 */
import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

// Base de l'API pour l'appel SERVEUR de NextAuth (authorize). Ce code s'execute
// dans la fonction serverless Vercel, PAS dans le navigateur : `process.env` y
// est lu au RUNTIME. Piege classique : si NEXT_PUBLIC_API_URL n'est pas defini
// cote serveur (ou vaut localhost), authorize() part sur 127.0.0.1 -> le GET
// /auth/session echoue -> NextAuth renvoie 401 alors que le login navigateur
// (cote client) touche bien la prod. On aligne donc la resolution sur le meme
// garde-fou que api-client, avec un defaut = le backend reellement en ligne.
const PROD_API_BASE = 'https://evo-log-backend-production.up.railway.app'

function resolveApiBase(): string {
  let base =
    process.env.API_URL || // prioritaire cote serveur si defini
    process.env.NEXT_PUBLIC_API_URL ||
    PROD_API_BASE
  // En production, ne JAMAIS viser une boucle locale depuis le serveur.
  if (process.env.NODE_ENV === 'production' && (base.includes('localhost') || base.includes('127.0.0.1'))) {
    base = PROD_API_BASE
  }
  return base.replace(/\/+$/, '')
}

const API_BASE = resolveApiBase()

// Retry borne face aux micro-fenêtres d'indisponibilité Railway (cold-start /
// redéploiement déclenché par l'auto-push). Un 502/503/504 vient du PROXY et
// n'a PAS atteint l'app : le retenter est sûr (pas de compteur de tentatives
// ni de rate-limit incrémentés). Une 4xx (401/403/422) vient de l'app -> on ne
// la retente JAMAIS. Max 3 essais (2 retries), backoff croissant 0.5s/1s.
async function fetchWithColdStartRetry(
  url: string,
  init: RequestInit,
  attempts = 3,
): Promise<Response> {
  let lastErr: unknown
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(url, init)
      const transient = res.status === 502 || res.status === 503 || res.status === 504
      if (!transient || i === attempts - 1) return res
    } catch (err) {
      // Erreur réseau (DNS, connexion refusée pendant un boot) : transitoire.
      if (i === attempts - 1) throw err
      lastErr = err
    }
    await new Promise((r) => setTimeout(r, 500 * (i + 1)))
  }
  throw lastErr
}

interface BackendSession {
  access_token?: string
  refresh_token?: string
  user_id?: number
  username?: string
  email?: string
  roles?: string[]
  company_id?: number | null
  modules_allowed?: string[]
  permissions?: string[]
  shared_modules?: string[]
  role_level?: number
  department_id?: number | null
  is_superuser?: boolean
  must_change_password?: boolean
}

/** Map backend -> objet NextAuth. Partagee par les deux voies d'entree (jalon
 *  deja authentifie / couple identifiant-mot de passe) pour qu'aucune ne oublie
 *  un champ RBAC. */
function toSessionUser(p: BackendSession, accessToken: string, refreshToken?: string) {
  return {
    id: String(p.user_id ?? ''),
    name: p.username,
    email: p.email,
    access_token: accessToken,
    refresh_token: refreshToken ?? null,
    roles: p.roles || [],
    company_id: p.company_id ?? null,
    modules_allowed: p.modules_allowed || [],
    // RBAC granulaire : permissions effectives (codes module.sous.action),
    // niveau hiérarchique, service commun par entreprise.
    permissions: p.permissions || [],
    shared_modules: p.shared_modules || [],
    role_level: p.role_level ?? 3,
    department_id: p.department_id ?? null,
    is_superuser: !!p.is_superuser,
    must_change_password: !!p.must_change_password,
  }
}

/** Aterrage par defaut selon les roles renvoyes par le backend. */
export function landingRouteFor(roles: string[]): string {
  if (roles.includes('CHAUFFEUR')) return '/chauffeur'
  if (roles.includes('ADMIN') || roles.includes('MANAGER')) return '/dashboard/global'
  if (roles.includes('MAGASINIER') || roles.includes('MAGASIN')) return '/magasin/dashboard'
  if (roles.includes('TRANSPORT') || roles.includes('DISPATCHER')) return '/transport/control'
  if (roles.includes('FINANCE')) return '/finance/overview'
  return '/dashboard/global'
}

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
        email: { label: "Email", type: "text" },
        // Jalon delivre par le formulaire de connexion apres verification du
        // mot de passe (et du code 2FA quand il y en a un).
        ticket: { label: "Session ticket", type: "text" },
      },
      async authorize(credentials) {
        // Toute la logique est enveloppee : une erreur reseau vers le backend
        // (cold start Railway, DNS, timeout) doit se traduire par un echec de
        // connexion propre (null -> NextAuth 401 + log serveur), JAMAIS par une
        // exception non capturee qui noie la vraie cause dans les logs Vercel.
        try {
          // Voie « jalon » : /login a deja ete appele par le navigateur. On
          // revalide le token aupres de GET /auth/session au lieu de renvoyer le
          // mot de passe : un deuxieme /login gonflerait le compteur de
          // tentatives (et le rate-limit) pour une seule connexion.
          if (credentials?.ticket) {
            const res = await fetchWithColdStartRetry(`${API_BASE}/api/v1/auth/session`, {
              headers: { Authorization: `Bearer ${credentials.ticket}` },
            })
            if (!res.ok) {
              console.error(`[auth] /session -> ${res.status} sur ${API_BASE}`)
              return null
            }
            const payload: BackendSession = await res.json()
            if (!payload?.access_token) return null
            return toSessionUser(payload, payload.access_token, payload.refresh_token)
          }

          // Call backend auth API
          const identifier = (credentials as any)?.email || credentials?.username
          const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: identifier,
              password: credentials?.password
            }),
          })

          if (!res.ok) {
            console.error(`[auth] /login -> ${res.status} sur ${API_BASE}`)
            return null
          }

          const user = await res.json()

          if (user && user.access_token) {
            return toSessionUser(user, user.access_token, user.refresh_token)
          }
          // 2FA active : le backend renvoie un jeton intermediaire, pas de
          // session. Le formulaire doit passer par /mfa puis revenir avec un
          // ticket ; on ne cree jamais de session sans le second facteur.
          return null
        } catch (err) {
          console.error(`[auth] authorize() exception (API_BASE=${API_BASE}) :`, err)
          return null
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as any).access_token
        token.refreshToken = (user as any).refresh_token
        token.roles = (user as any).roles || []
        token.companyId = (user as any).company_id
        token.modulesAllowed = (user as any).modules_allowed || []
        token.permissions = (user as any).permissions || []
        token.sharedModules = (user as any).shared_modules || []
        token.roleLevel = (user as any).role_level ?? 3
        token.departmentId = (user as any).department_id ?? null
        token.isSuperuser = !!(user as any).is_superuser
        token.mustChangePassword = !!(user as any).must_change_password
      }
      return token
    },
    async session({ session, token }: any) {
      session.accessToken = token.accessToken as string;
      session.refreshToken = token.refreshToken as string;
      if (session.user) {
        // AuthProvider lit session.user.accessToken : injecter sur user ET session
        session.user.accessToken = token.accessToken;
        session.user.refreshToken = token.refreshToken;
        session.user.roles = token.roles || [];
        session.user.company_id = token.companyId;
        session.user.modules_allowed = token.modulesAllowed || [];
        session.user.permissions = token.permissions || [];
        session.user.shared_modules = token.sharedModules || [];
        session.user.role_level = token.roleLevel ?? 3;
        session.user.department_id = token.departmentId ?? null;
        session.user.is_superuser = !!token.isSuperuser;
        session.user.must_change_password = !!token.mustChangePassword;
      }
      return session;
    },
  },
  pages: {
    signIn: '/login',
    signOut: '/login',
    error: '/login',
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: process.env.NEXTAUTH_SECRET,
}