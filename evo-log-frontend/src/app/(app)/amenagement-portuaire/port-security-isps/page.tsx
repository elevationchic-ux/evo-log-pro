'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreIspsRecord } from '@/components/amenagement-portuaire/registres_expansion';

export default function PageIspsRecord() {
  return <RegistreGenerique config={registreIspsRecord} />;
}
