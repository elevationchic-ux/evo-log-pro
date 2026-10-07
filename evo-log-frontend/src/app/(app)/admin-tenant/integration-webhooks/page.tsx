'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmtIntegrationWebhook } from '@/components/admin-tenant/registres_c';

export default function PageAdmtIntegrationWebhook() {
  return <RegistreGenerique config={registreAdmtIntegrationWebhook} />;
}
