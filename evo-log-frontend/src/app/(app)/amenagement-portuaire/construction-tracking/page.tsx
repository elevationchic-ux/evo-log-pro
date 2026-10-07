'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreConstructionProgress } from '@/components/amenagement-portuaire/registres_expansion';

export default function PageConstructionProgress() {
  return <RegistreGenerique config={registreConstructionProgress} />;
}
