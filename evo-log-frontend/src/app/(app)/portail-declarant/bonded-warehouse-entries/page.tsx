'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclBondedWarehouseEntry } from '@/components/portail-declarant/registres_c';

export default function PageDeclBondedWarehouseEntry() {
  return <RegistreGenerique config={registreDeclBondedWarehouseEntry} />;
}
