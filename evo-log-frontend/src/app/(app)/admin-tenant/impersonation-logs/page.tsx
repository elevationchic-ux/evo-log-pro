'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtImpersonationLog } from '@/components/admin-tenant/registres_c';

export default function PageAdmtImpersonationLog() {
  return <RegistreGenerique config={registreAdmtImpersonationLog} />;
}
