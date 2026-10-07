'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechPreventivePlan } from '@/components/portail-technicien/registres_c';

export default function PageTechPreventivePlan() {
  return <RegistreGenerique config={registreTechPreventivePlan} />;
}
