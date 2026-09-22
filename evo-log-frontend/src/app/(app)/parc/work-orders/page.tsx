"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function ParcWorkOrdersPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/parc/worEVO-orders/create"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground text-sm">Redirection vers les Ordres de Travail...</div>;
}
