'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclCustomsInvoice } from '@/components/portail-declarant/registres_c';

export default function PageDeclCustomsInvoice() {
  return <RegistreGenerique config={registreDeclCustomsInvoice} />;
}
