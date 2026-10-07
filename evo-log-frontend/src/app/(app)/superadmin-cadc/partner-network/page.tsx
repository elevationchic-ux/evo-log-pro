'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechnologyPartner } from '@/components/superadmin-cadc/registres';

export default function PageTechnologyPartner() {
  return <RegistreGenerique config={registreTechnologyPartner} />;
}
