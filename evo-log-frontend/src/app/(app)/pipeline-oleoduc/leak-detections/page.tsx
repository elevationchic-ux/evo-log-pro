'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLeakDetection } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineLeakDetection() {
  return <RegistreGenerique config={registreLeakDetection} />;
}
