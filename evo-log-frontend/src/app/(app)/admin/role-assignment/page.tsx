"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
export default function RoleAssignmentPage() {
  const router = useRouter();
  useEffect(() => { router.replace("/admin/configuration-des-roles-rbac"); }, [router]);
  return <div className="p-8 text-center text-muted-foreground text-sm">Redirection vers la gestion des rÃ´les RBAC...</div>;
}
