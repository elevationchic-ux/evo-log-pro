'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechnicalVisit } from '@/components/parc-vehicules/registres';

export default function PageTechnicalVisit() {
  return <RegistreGenerique config={registreTechnicalVisit} />;
}
