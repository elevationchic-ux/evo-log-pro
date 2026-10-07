'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvCategory } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvCategory() {
  return <RegistreGenerique config={registreProvCategory} />;
}
