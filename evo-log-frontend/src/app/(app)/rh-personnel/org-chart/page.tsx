'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreOrgUnit } from '@/components/rh-personnel/registres';

export default function PageOrgUnit() {
  return <RegistreGenerique config={registreOrgUnit} />;
}
