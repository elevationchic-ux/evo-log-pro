'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfCargoSeal } from '@/components/portail-chauffeur/registres_c';

export default function PageChfCargoSeal() {
  return <RegistreGenerique config={registreChfCargoSeal} />;
}
