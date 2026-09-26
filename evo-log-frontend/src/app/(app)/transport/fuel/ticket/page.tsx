"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function TransportFuelTicketPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/transport/saisie-ticket-carburant"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground">Redirection vers la saisie de ticket carburant...</div>;
}
