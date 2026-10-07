'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfTyreCheck } from '@/components/portail-chauffeur/registres_c';

export default function PageChfTyreCheck() {
  return <RegistreGenerique config={registreChfTyreCheck} />;
}
