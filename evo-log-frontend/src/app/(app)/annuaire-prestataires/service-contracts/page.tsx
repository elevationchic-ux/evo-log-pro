'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvServiceContract } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvServiceContract() {
  return <RegistreGenerique config={registreProvServiceContract} />;
}
