'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreKpiDefinition } from '@/components/reports-bi/registres';

export default function PageKpiDefinition() {
  return <RegistreGenerique config={registreKpiDefinition} />;
}
