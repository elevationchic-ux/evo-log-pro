'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRptcAdHocQuery } from '@/components/reports-bi/registres_c';

export default function PageRptcAdHocQuery() {
  return <RegistreGenerique config={registreRptcAdHocQuery} />;
}
