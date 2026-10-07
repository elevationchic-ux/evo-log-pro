'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAdmCUsageMetering } from '@/components/admin-saas/registres_c';

export default function PageAdmCUsageMetering() {
  return <RegistreGenerique config={registreAdmCUsageMetering} />;
}
