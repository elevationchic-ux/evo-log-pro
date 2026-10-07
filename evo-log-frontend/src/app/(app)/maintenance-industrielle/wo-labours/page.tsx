'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWoLabour } from '@/components/maintenance-industrielle/registres';

export default function PageWorkOrderLabour() {
  return <RegistreGenerique config={registreWoLabour} />;
}
