'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreStockReturn } from '@/components/magasin-stock/registres';

export default function PageStockReturn() {
  return <RegistreGenerique config={registreStockReturn} />;
}
