'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclPackingList } from '@/components/portail-declarant/registres_c';

export default function PageDeclPackingList() {
  return <RegistreGenerique config={registreDeclPackingList} />;
}
