/**
 * NextAuth v4 configuration for EVO-LOG frontend
 * Synchronized with backend RBAC system
 */
import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
        email: { label: "Email", type: "text" }
      },
      async authorize(credentials) {
        // Call backend auth API
        const identifier = (credentials as any)?.email || credentials?.username
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: identifier,
            password: credentials?.password
          }),
        })

        if (!res.ok) {
          return null
        }

        const user = await res.json()

        if (user && user.access_token) {
          return {
            id: String(user.user_id),
            name: user.username,
            email: user.email,
            access_token: user.access_token,
            refresh_token: user.refresh_token,
            roles: user.roles || [],
            company_id: user.company_id,
            modules_allowed: user.modules_allowed || [],
            // RBAC granulaire : permissions effectives (codes module.sous.action),
            // niveau hiérarchique, service commun par entreprise.
            permissions: user.permissions || [],
            shared_modules: user.shared_modules || [],
            role_level: user.role_level ?? 3,
            department_id: user.department_id ?? null,
            is_superuser: !!user.is_superuser,
            must_change_password: !!user.must_change_password,
          }
        }
        return null
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
    async session({ session, token }) {
      (session as any).accessToken = token.accessToken as string
      (session as any).refreshToken = token.refreshToken as string
      if (session.user) {
        // AuthProvider lit session.user.accessToken  injecter sur user ET session
        (session.user as any).accessToken = (token as any).accessToken
        ;(session.user as any).refreshToken = (token as any).refreshToken
        (session.user as any).roles = (token as any).roles || []
        ;(session.user as any).company_id = (token as any).companyId
        ;(session.user as any).modules_allowed = (token as any).modulesAllowed || []
        ;(session.user as any).permissions = (token as any).permissions || []
        ;(session.user as any).shared_modules = (token as any).sharedModules || []
        ;(session.user as any).role_level = (token as any).roleLevel ?? 3
        ;(session.user as any).department_id = (token as any).departmentId ?? null
        ;(session.user as any).is_superuser = !!(token as any).isSuperuser
        ;(session.user as any).must_change_password = !!(token as any).mustChangePassword
      }
      return session
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