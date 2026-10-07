'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDepObjective } from '@/components/departement/registres_d5';

export default function PageDepObjective() {
  return <RegistreGenerique config={registreDepObjective} />;
}
