'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWoPart } from '@/components/maintenance-industrielle/registres';

export default function PageWorkOrderPart() {
  return <RegistreGenerique config={registreWoPart} />;
}
