'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRhCDisciplinaryRecord } from '@/components/rh-personnel/registres_c';

export default function PageRhCDisciplinaryRecord() {
  return <RegistreGenerique config={registreRhCDisciplinaryRecord} />;
}
