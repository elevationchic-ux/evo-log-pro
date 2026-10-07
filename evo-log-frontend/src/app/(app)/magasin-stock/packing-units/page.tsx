'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePackingUnit } from '@/components/magasin-stock/registres';

export default function PagePackingUnit() {
  return <RegistreGenerique config={registrePackingUnit} />;
}
