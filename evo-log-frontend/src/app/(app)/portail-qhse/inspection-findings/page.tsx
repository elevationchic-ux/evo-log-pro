'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspInspectionFinding } from '@/components/portail-qhse/registres_c';

export default function PageQspInspectionFinding() {
  return <RegistreGenerique config={registreQspInspectionFinding} />;
}
