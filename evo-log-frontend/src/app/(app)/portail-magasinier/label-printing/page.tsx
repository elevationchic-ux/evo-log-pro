'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcLabelPrint } from '@/components/portail-magasinier/registres_c';

export default function PageMagcLabelPrint() {
  return <RegistreGenerique config={registreMagcLabelPrint} />;
}
