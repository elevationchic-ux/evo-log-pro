'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmployeeSkill } from '@/components/rh-personnel/registres';

export default function PageEmployeeSkill() {
  return <RegistreGenerique config={registreEmployeeSkill} />;
}
