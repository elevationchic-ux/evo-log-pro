'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtDataResidency } from '@/components/admin-tenant/registres_c';

export default function PageAdmtDataResidency() {
  return <RegistreGenerique config={registreAdmtDataResidency} />;
}
