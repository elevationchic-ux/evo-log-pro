'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAnomalyRecord } from '@/components/reports-bi/registres';

export default function PageAnomalyRecord() {
  return <RegistreGenerique config={registreAnomalyRecord} />;
}
