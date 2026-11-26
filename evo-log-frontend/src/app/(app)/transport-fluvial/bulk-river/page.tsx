'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialBulkOperation } from '@/components/transport-fluvial/registres';

export default function PageFluvialBulkOperation() {
  return <RegistreGenerique config={registreFluvialBulkOperation} />;
}
