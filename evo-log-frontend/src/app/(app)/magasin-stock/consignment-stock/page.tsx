'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreConsignmentStock } from '@/components/magasin-stock/registres';

export default function PageConsignmentStock() {
  return <RegistreGenerique config={registreConsignmentStock} />;
}
