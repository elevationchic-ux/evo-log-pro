'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmCApiToken } from '@/components/admin-saas/registres_c';

export default function PageAdmCApiToken() {
  return <RegistreGenerique config={registreAdmCApiToken} />;
}
