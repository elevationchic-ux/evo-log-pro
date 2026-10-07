'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePlatformIncident } from '@/components/superadmin-cadc/registres';

export default function PagePlatformIncident() {
  return <RegistreGenerique config={registrePlatformIncident} />;
}
