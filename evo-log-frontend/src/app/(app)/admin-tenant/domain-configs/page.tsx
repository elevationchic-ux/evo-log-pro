'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtDomainConfig } from '@/components/admin-tenant/registres_c';

export default function PageAdmtDomainConfig() {
  return <RegistreGenerique config={registreAdmtDomainConfig} />;
}
