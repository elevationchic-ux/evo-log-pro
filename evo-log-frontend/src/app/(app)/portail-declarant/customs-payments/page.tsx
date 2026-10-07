'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclCustomsPayment } from '@/components/portail-declarant/registres_c';

export default function PageDeclCustomsPayment() {
  return <RegistreGenerique config={registreDeclCustomsPayment} />;
}
