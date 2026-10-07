'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTenantWebhook } from '@/components/admin-saas/registres';

export default function PageTenantWebhook() {
  return <RegistreGenerique config={registreTenantWebhook} />;
}
