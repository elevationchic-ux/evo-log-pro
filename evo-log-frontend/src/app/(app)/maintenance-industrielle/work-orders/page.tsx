'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWorkOrder } from '@/components/maintenance-industrielle/registres';

export default function PageWorkOrder() {
  return <RegistreGenerique config={registreWorkOrder} />;
}
