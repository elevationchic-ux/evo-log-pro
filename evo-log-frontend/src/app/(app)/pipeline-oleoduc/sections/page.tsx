'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSection } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineSection() {
  return <RegistreGenerique config={registreSection} />;
}
