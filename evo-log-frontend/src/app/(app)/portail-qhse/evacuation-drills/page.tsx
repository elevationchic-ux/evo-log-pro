'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspEvacuationDrill } from '@/components/portail-qhse/registres_c';

export default function PageQspEvacuationDrill() {
  return <RegistreGenerique config={registreQspEvacuationDrill} />;
}
