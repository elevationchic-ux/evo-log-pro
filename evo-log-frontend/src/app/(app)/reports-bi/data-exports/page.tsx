'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRptcDataExport } from '@/components/reports-bi/registres_c';

export default function PageRptcDataExport() {
  return <RegistreGenerique config={registreRptcDataExport} />;
}
