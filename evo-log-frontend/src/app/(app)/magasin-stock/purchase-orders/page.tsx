'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePurchaseOrderDeep } from '@/components/magasin-stock/registres';

export default function PagePurchaseOrderDeep() {
  return <RegistreGenerique config={registrePurchaseOrderDeep} />;
}
