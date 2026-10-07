'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTenantOnboarding } from '@/components/admin-saas/registres';

export default function PageTenantOnboarding() {
  return <RegistreGenerique config={registreTenantOnboarding} />;
}
