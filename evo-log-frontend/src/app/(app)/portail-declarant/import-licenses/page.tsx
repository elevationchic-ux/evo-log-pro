'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclImportLicense } from '@/components/portail-declarant/registres_c';

export default function PageDeclImportLicense() {
  return <RegistreGenerique config={registreDeclImportLicense} />;
}
