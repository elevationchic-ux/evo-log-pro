"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function TransportPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/transport/control"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground">Redirection vers le Poste de Contrôle Transport...</div>;
}
