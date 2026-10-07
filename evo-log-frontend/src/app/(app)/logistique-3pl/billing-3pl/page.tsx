'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplInvoice } from '@/components/logistique-3pl/registres';

export default function PageTplInvoice() {
  return <RegistreGenerique config={registreTplInvoice} />;
}
