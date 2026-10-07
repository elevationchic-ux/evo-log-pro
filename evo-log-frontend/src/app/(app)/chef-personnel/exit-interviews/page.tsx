'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpExitInterview } from '@/components/chef-personnel/registres_c';

export default function PageChpExitInterview() {
  return <RegistreGenerique config={registreChpExitInterview} />;
}
