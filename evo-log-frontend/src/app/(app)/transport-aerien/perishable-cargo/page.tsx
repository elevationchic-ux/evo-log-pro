'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePerishableCargo } from '@/components/transport-aerien/registres_b';

export default function PagePerishableCargo() {
  return <RegistreGenerique config={registrePerishableCargo} />;
}
