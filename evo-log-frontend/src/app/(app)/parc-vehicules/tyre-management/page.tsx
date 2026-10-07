'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTyreRecord } from '@/components/parc-vehicules/registres';

export default function PageTyreRecord() {
  return <RegistreGenerique config={registreTyreRecord} />;
}
