'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWorkforcePlan } from '@/components/rh-personnel/registres';

export default function PageWorkforcePlan() {
  return <RegistreGenerique config={registreWorkforcePlan} />;
}
