'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommCommissionStatement } from '@/components/portail-commercial/registres_c';

export default function PageCommCommissionStatement() {
  return <RegistreGenerique config={registreCommCommissionStatement} />;
}
