'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDemurrageCase } from '@/components/port-operations/registres';

export default function PageDemurrageCase() {
  return <RegistreGenerique config={registreDemurrageCase} />;
}
