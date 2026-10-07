'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplCarrierRate } from '@/components/logistique-3pl/registres_b';

export default function PageTplCarrierRate() {
  return <RegistreGenerique config={registreTplCarrierRate} />;
}
