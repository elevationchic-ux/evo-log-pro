'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMeteringPoint } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineMeteringPoint() {
  return <RegistreGenerique config={registreMeteringPoint} />;
}
