'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpTrainingPlan } from '@/components/chef-personnel/registres_c';

export default function PageChpTrainingPlan() {
  return <RegistreGenerique config={registreChpTrainingPlan} />;
}
