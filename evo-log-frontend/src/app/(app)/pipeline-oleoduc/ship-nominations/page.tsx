'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreShipNomination } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineShipNomination() {
  return <RegistreGenerique config={registreShipNomination} />;
}
