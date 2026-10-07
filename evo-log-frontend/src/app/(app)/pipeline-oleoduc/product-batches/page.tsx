'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProductBatch } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineProductBatch() {
  return <RegistreGenerique config={registreProductBatch} />;
}
