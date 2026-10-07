'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRca } from '@/components/maintenance-industrielle/registres';

export default function PageRootCauseAnalysis() {
  return <RegistreGenerique config={registreRca} />;
}
