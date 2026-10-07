'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpDocumentUpload } from '@/components/portail-employe/registres_c';

export default function PageEmpDocumentUpload() {
  return <RegistreGenerique config={registreEmpDocumentUpload} />;
}
