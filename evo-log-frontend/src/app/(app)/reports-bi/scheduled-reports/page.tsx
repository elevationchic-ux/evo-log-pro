'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRptcScheduledReport } from '@/components/reports-bi/registres_c';

export default function PageRptcScheduledReport() {
  return <RegistreGenerique config={registreRptcScheduledReport} />;
}
