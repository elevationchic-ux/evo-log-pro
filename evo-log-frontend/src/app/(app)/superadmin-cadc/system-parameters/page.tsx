'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSaCSystemParameter } from '@/components/superadmin-cadc/registres_c';

export default function PageSaCSystemParameter() {
  return <RegistreGenerique config={registreSaCSystemParameter} />;
}
