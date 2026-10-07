'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclIncotermsRecord } from '@/components/portail-declarant/registres_c';

export default function PageDeclIncotermsRecord() {
  return <RegistreGenerique config={registreDeclIncotermsRecord} />;
}
