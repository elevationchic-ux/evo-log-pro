'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSaasApiKey } from '@/components/admin-saas/registres';

export default function PageSaasApiKey() {
  return <RegistreGenerique config={registreSaasApiKey} />;
}
