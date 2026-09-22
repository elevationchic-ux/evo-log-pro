// src/app/(auth)/layout.tsx
// Layout gÃ©nÃ©rique pour toutes les pages d'authentification
// Chaque page gÃ¨re sa propre "carte" et mise en page interne

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
