'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTallySheet } from '@/components/port-operations/registres';

export default function PageTallySheet() {
  return <RegistreGenerique config={registreTallySheet} />;
}
