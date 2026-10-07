'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreStorageTank } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineStorageTank() {
  return <RegistreGenerique config={registreStorageTank} />;
}
