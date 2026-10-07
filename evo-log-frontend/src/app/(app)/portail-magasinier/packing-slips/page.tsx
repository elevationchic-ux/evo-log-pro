'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcPackingSlip } from '@/components/portail-magasinier/registres_c';

export default function PageMagcPackingSlip() {
  return <RegistreGenerique config={registreMagcPackingSlip} />;
}
