'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvPriceList } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvPriceList() {
  return <RegistreGenerique config={registreProvPriceList} />;
}
