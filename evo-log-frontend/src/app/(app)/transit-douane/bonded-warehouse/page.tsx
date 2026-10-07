'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBondedWarehouse } from '@/components/transit-douane/registres';

export default function PageBondedWarehouse() {
  return <RegistreGenerique config={registreBondedWarehouse} />;
}
