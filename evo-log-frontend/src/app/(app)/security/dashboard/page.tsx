"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function SecurityDashboardPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/security/notifications"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground text-sm">Redirection vers le Centre de Sécurité...</div>;
}
