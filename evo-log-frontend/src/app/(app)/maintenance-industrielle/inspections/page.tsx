'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreInspection } from '@/components/maintenance-industrielle/registres';

export default function PageRegulatoryInspection() {
  return <RegistreGenerique config={registreInspection} />;
}
