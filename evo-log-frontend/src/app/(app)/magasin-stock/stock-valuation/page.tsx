'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreStockValuation } from '@/components/magasin-stock/registres';

export default function PageStockValuation() {
  return <RegistreGenerique config={registreStockValuation} />;
}
