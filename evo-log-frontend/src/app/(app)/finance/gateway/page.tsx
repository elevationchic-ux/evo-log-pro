"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function FinanceGatewayPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/gateway"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground text-sm">Redirection vers le Gateway & Intégrations...</div>;
}
