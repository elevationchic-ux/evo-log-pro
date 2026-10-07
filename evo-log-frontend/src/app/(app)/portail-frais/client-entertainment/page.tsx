'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraClientEntertainment } from '@/components/portail-frais/registres_c';

export default function PageFraClientEntertainment() {
  return <RegistreGenerique config={registreFraClientEntertainment} />;
}
