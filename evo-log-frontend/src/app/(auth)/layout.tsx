// src/app/(auth)/layout.tsx
// Layout générique pour toutes les pages d'authentification
// Chaque page gère sa propre "carte" et mise en page interne

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
