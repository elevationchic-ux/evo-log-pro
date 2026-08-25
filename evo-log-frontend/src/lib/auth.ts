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
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // In production, this would call the backend API
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: credentials?.username,
            password: credentials?.password
          }),
        })

        const user = await res.json()

        if (res.ok && user) {
          return {
            id: user.user_id,
            name: user.username,
            email: user.email,
            access_token: user.access_token,
            refresh_token: user.refresh_token,
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
      }
      return token
    },
    async session({ session, token }) {
      (session as any).accessToken = token.accessToken as string
      (session as any).refreshToken = token.refreshToken as string
      return session
    },
  },
  pages: {
    signIn: '/(auth)/login',
    signOut: '/(auth)/login',
    error: '/(auth)/login',
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: process.env.NEXTAUTH_SECRET,
}