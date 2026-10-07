'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraConferenceFee } from '@/components/portail-frais/registres_c';

export default function PageFraConferenceFee() {
  return <RegistreGenerique config={registreFraConferenceFee} />;
}
