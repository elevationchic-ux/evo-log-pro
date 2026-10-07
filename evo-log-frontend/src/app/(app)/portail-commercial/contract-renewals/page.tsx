'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommContractRenewal } from '@/components/portail-commercial/registres_c';

export default function PageCommContractRenewal() {
  return <RegistreGenerique config={registreCommContractRenewal} />;
}
