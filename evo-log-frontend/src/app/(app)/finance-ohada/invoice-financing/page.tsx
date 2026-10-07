'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFincInvoiceFinancing } from '@/components/finance-ohada/registres_c';

export default function PageFincInvoiceFinancing() {
  return <RegistreGenerique config={registreFincInvoiceFinancing} />;
}
