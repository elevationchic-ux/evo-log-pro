'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCargoHandlingPlan } from '@/components/port-operations/registres';

export default function PageCargoHandlingPlan() {
  return <RegistreGenerique config={registreCargoHandlingPlan} />;
}
