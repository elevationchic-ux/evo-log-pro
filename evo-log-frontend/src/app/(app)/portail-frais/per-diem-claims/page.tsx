'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraPerDiemClaim } from '@/components/portail-frais/registres_c';

export default function PageFraPerDiemClaim() {
  return <RegistreGenerique config={registreFraPerDiemClaim} />;
}
