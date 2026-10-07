'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRegExport } from '@/components/tracabilite/registres';

export default function PageRegulatoryTraceExport() {
  return <RegistreGenerique config={registreRegExport} />;
}
