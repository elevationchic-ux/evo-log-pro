'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpCandidateSelection } from '@/components/chef-personnel/registres_c';

export default function PageChpCandidateSelection() {
  return <RegistreGenerique config={registreChpCandidateSelection} />;
}
