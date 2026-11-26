'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTrainingPlan } from '@/components/rh-personnel/registres';

export default function PageTrainingPlan() {
  return <RegistreGenerique config={registreTrainingPlan} />;
}
