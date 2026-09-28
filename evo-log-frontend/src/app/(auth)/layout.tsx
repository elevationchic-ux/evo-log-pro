// src/app/(auth)/layout.tsx
// Layout générique pour toutes les pages d'authentification
// Chaque page gère sa propre "carte" et mise en page interne

// Les pages auth dépendent de next-auth/react (session) et ne doivent jamais
// être pré-rendues statiquement — forcer le rendu dynamique.
export const dynamic = 'force-dynamic';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
