'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreYardOperation } from '@/components/port-operations/registres';

export default function PageYardOperation() {
  return <RegistreGenerique config={registreYardOperation} />;
}
