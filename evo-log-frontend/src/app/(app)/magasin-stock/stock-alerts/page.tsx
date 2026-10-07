'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreStockAlert } from '@/components/magasin-stock/registres';

export default function PageStockAlert() {
  return <RegistreGenerique config={registreStockAlert} />;
}
