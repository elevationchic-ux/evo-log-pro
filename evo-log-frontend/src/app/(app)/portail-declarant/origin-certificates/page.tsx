'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclOriginCertificate } from '@/components/portail-declarant/registres_c';

export default function PageDeclOriginCertificate() {
  return <RegistreGenerique config={registreDeclOriginCertificate} />;
}
