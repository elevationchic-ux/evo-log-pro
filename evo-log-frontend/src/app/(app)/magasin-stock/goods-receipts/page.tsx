'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagasinbGoodsReceipt } from '@/components/magasin-stock/registres_b';

export default function PageMagasinbGoodsReceipt() {
  return <RegistreGenerique config={registreMagasinbGoodsReceipt} />;
}
