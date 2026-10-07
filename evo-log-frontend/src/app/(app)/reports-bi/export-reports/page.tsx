'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreReportExport } from '@/components/reports-bi/registres';

export default function PageReportExport() {
  return <RegistreGenerique config={registreReportExport} />;
}
