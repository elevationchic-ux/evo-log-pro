'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmCTenantInvite } from '@/components/admin-saas/registres_c';

export default function PageAdmCTenantInvite() {
  return <RegistreGenerique config={registreAdmCTenantInvite} />;
}
