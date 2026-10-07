'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraCardTransaction } from '@/components/portail-frais/registres_c';

export default function PageFraCardTransaction() {
  return <RegistreGenerique config={registreFraCardTransaction} />;
}
