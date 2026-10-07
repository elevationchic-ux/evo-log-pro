'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePlatformAudit } from '@/components/superadmin-cadc/registres';

export default function PagePlatformAudit() {
  return <RegistreGenerique config={registrePlatformAudit} />;
}
