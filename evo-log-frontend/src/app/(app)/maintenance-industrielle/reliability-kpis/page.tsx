'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreReliabilityKpi } from '@/components/maintenance-industrielle/registres';

export default function PageReliabilityKpi() {
  return <RegistreGenerique config={registreReliabilityKpi} />;
}
