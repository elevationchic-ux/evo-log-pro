'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreB2bCPriceList } from '@/components/client-b2b/registres_c';

export default function PageB2bCPriceList() {
  return <RegistreGenerique config={registreB2bCPriceList} />;
}
