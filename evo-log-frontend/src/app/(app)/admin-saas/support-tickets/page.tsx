'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePlatformTicket } from '@/components/admin-saas/registres';

export default function PagePlatformTicket() {
  return <RegistreGenerique config={registrePlatformTicket} />;
}
