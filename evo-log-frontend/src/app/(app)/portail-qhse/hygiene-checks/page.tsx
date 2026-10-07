'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspHygieneCheck } from '@/components/portail-qhse/registres_c';

export default function PageQspHygieneCheck() {
  return <RegistreGenerique config={registreQspHygieneCheck} />;
}
