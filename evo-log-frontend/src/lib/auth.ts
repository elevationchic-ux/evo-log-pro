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
      }
      return token
    },
    async session({ session, token }) {
      (session as any).accessToken = token.accessToken as string
      (session as any).refreshToken = token.refreshToken as string
      if (session.user) {
        (session.user as any).roles = (token as any).roles || []
        ;(session.user as any).company_id = (token as any).companyId
        ;(session.user as any).modules_allowed = (token as any).modulesAllowed || []
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