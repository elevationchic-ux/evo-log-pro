"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function FinancePayrollPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/rh/paie"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground text-sm">Redirection vers la Gestion de la Paie RH...</div>;
}
