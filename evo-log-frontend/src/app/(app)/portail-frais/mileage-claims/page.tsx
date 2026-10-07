'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraMileageClaim } from '@/components/portail-frais/registres_c';

export default function PageFraMileageClaim() {
  return <RegistreGenerique config={registreFraMileageClaim} />;
}
