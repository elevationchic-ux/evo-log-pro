'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRptcReportTemplate } from '@/components/reports-bi/registres_c';

export default function PageRptcReportTemplate() {
  return <RegistreGenerique config={registreRptcReportTemplate} />;
}
