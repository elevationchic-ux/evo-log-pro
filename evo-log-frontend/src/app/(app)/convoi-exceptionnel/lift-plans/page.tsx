'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLLiftPlan } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftLiftPlan() {
  return <RegistreGenerique config={registreHLLiftPlan} />;
}
