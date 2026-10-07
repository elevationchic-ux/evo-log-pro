'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2LiftPlan } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2LiftPlan() {
  return <RegistreGenerique config={registreHeavy2LiftPlan} />;
}
