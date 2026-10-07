'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDepProject } from '@/components/departement/registres_d5';

export default function PageDepProject() {
  return <RegistreGenerique config={registreDepProject} />;
}
