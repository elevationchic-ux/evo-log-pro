'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreGatePass } from '@/components/port-operations/registres';

export default function PageGatePass() {
  return <RegistreGenerique config={registreGatePass} />;
}
