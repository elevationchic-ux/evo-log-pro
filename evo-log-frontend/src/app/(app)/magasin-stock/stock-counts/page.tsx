'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagasinbStockCount } from '@/components/magasin-stock/registres_b';

export default function PageMagasinbStockCount() {
  return <RegistreGenerique config={registreMagasinbStockCount} />;
}
