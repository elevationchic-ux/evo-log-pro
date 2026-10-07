'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePumpStation } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelinePumpStation() {
  return <RegistreGenerique config={registrePumpStation} />;
}
