"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function TransportMaintenancePage() {
  const router = useRouter();
  useEffect(() => { router.replace("/maintenance"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground text-sm">Redirection vers le Module Maintenance...</div>;
}
