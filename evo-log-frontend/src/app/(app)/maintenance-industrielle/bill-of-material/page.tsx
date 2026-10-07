'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBom } from '@/components/maintenance-industrielle/registres';

export default function PageBillOfMaterial() {
  return <RegistreGenerique config={registreBom} />;
}
