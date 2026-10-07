'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRptcOlapCube } from '@/components/reports-bi/registres_c';

export default function PageRptcOlapCube() {
  return <RegistreGenerique config={registreRptcOlapCube} />;
}
