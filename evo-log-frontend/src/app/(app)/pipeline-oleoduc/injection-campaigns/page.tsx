'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreInjectCampaign } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineInjectionCampaign() {
  return <RegistreGenerique config={registreInjectCampaign} />;
}
