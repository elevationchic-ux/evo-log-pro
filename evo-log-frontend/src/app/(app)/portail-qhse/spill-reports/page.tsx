'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspSpillReport } from '@/components/portail-qhse/registres_c';

export default function PageQspSpillReport() {
  return <RegistreGenerique config={registreQspSpillReport} />;
}
