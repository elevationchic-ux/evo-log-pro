'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtWhiteLabelConfig } from '@/components/admin-tenant/registres_c';

export default function PageAdmtWhiteLabelConfig() {
  return <RegistreGenerique config={registreAdmtWhiteLabelConfig} />;
}
