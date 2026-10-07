'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmployeeExit } from '@/components/rh-personnel/registres';

export default function PageEmployeeExit() {
  return <RegistreGenerique config={registreEmployeeExit} />;
}
