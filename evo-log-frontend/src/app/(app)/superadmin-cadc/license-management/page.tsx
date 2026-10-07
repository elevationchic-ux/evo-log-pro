'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSoftwareLicense } from '@/components/superadmin-cadc/registres';

export default function PageSoftwareLicense() {
  return <RegistreGenerique config={registreSoftwareLicense} />;
}
