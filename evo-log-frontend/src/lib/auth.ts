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