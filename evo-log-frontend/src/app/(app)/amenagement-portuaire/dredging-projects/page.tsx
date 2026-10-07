'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAmgtbDredgingProject } from '@/components/amenagement-portuaire/registres_b';

export default function PageAmgtbDredgingProject() {
  return <RegistreGenerique config={registreAmgtbDredgingProject} />;
}
