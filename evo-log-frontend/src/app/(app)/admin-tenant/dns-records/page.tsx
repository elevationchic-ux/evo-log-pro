'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtDnsRecord } from '@/components/admin-tenant/registres_c';

export default function PageAdmtDnsRecord() {
  return <RegistreGenerique config={registreAdmtDnsRecord} />;
}
