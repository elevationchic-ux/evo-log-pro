'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTowageOperation } from '@/components/port-operations/registres';

export default function PageTowageOperation() {
  return <RegistreGenerique config={registreTowageOperation} />;
}
