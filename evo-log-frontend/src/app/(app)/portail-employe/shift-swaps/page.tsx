'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEmpShiftSwap } from '@/components/portail-employe/registres_c';

export default function PageEmpShiftSwap() {
  return <RegistreGenerique config={registreEmpShiftSwap} />;
}
