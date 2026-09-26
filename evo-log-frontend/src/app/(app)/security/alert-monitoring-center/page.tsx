"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function SecurityAlertMonitoringCenter() {
  const router = useRouter();
  useEffect(() => { router.replace("/security/alert-monitoring"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground text-sm">Redirection vers le Monitoring des Alertes...</div>;
}
