'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmergencyPlan } from '@/components/qhse-securite/registres';

export default function PageEmergencyPlan() {
  return <RegistreGenerique config={registreEmergencyPlan} />;
}
