'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWhiteLabel } from '@/components/admin-saas/registres';

export default function PageWhiteLabel() {
  return <RegistreGenerique config={registreWhiteLabel} />;
}
