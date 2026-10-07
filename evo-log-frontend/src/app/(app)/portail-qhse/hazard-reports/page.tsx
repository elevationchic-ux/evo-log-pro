'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspHazardReport } from '@/components/portail-qhse/registres_c';

export default function PageQspHazardReport() {
  return <RegistreGenerique config={registreQspHazardReport} />;
}
