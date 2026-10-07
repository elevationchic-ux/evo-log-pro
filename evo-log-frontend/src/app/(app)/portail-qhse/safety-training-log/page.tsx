'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspSafetyTrainingLog } from '@/components/portail-qhse/registres_c';

export default function PageQspSafetyTrainingLog() {
  return <RegistreGenerique config={registreQspSafetyTrainingLog} />;
}
