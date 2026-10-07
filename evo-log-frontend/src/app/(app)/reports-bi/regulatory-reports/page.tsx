'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRegulatoryReport } from '@/components/reports-bi/registres';

export default function PageRegulatoryReport() {
  return <RegistreGenerique config={registreRegulatoryReport} />;
}
