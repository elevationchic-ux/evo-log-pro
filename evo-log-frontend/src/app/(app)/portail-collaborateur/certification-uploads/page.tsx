'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollCertificationUpload } from '@/components/portail-collaborateur/registres_c';

export default function PageCollCertificationUpload() {
  return <RegistreGenerique config={registreCollCertificationUpload} />;
}
