'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtTenantBackup } from '@/components/admin-tenant/registres_c';

export default function PageAdmtTenantBackup() {
  return <RegistreGenerique config={registreAdmtTenantBackup} />;
}
