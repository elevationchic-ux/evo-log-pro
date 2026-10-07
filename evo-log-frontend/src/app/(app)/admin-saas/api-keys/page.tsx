'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTenantApiKey } from '@/components/admin-saas/registres';

export default function PageTenantApiKey() {
  return <RegistreGenerique config={registreTenantApiKey} />;
}
