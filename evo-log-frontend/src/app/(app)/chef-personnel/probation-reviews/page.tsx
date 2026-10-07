'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpProbationReview } from '@/components/chef-personnel/registres_c';

export default function PageChpProbationReview() {
  return <RegistreGenerique config={registreChpProbationReview} />;
}
