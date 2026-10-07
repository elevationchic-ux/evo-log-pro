'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSerializedPart } from '@/components/maintenance-industrielle/registres';

export default function PageSerializedPart() {
  return <RegistreGenerique config={registreSerializedPart} />;
}
