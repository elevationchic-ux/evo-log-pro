'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRiverDepthSurvey } from '@/components/transport-fluvial/registres';

export default function PageRiverDepthSurvey() {
  return <RegistreGenerique config={registreRiverDepthSurvey} />;
}
