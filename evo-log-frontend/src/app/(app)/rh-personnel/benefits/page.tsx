'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmployeeBenefit } from '@/components/rh-personnel/registres';

export default function PageEmployeeBenefit() {
  return <RegistreGenerique config={registreEmployeeBenefit} />;
}
