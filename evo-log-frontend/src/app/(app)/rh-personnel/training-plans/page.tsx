'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRhCTrainingPlan } from '@/components/rh-personnel/registres_c';

export default function PageRhCTrainingPlan() {
  return <RegistreGenerique config={registreRhCTrainingPlan} />;
}
