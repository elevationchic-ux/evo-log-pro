'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSaCPlatformAlert } from '@/components/superadmin-cadc/registres_c';

export default function PageSaCPlatformAlert() {
  return <RegistreGenerique config={registreSaCPlatformAlert} />;
}
