'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLProject } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftProject() {
  return <RegistreGenerique config={registreHLProject} />;
}
