'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtUsageQuota } from '@/components/admin-tenant/registres_c';

export default function PageAdmtUsageQuota() {
  return <RegistreGenerique config={registreAdmtUsageQuota} />;
}
