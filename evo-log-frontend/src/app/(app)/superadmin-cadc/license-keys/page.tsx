'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSaCLicenseKey } from '@/components/superadmin-cadc/registres_c';

export default function PageSaCLicenseKey() {
  return <RegistreGenerique config={registreSaCLicenseKey} />;
}
