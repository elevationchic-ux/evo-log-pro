'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraVatRecovery } from '@/components/portail-frais/registres_c';

export default function PageFraVatRecovery() {
  return <RegistreGenerique config={registreFraVatRecovery} />;
}
