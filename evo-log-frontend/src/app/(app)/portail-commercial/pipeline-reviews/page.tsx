'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommPipelineReview } from '@/components/portail-commercial/registres_c';

export default function PageCommPipelineReview() {
  return <RegistreGenerique config={registreCommPipelineReview} />;
}
