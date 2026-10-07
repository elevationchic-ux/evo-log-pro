'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclExportLicense } from '@/components/portail-declarant/registres_c';

export default function PageDeclExportLicense() {
  return <RegistreGenerique config={registreDeclExportLicense} />;
}
