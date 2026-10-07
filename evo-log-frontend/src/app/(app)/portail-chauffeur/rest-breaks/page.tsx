'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfRestBreak } from '@/components/portail-chauffeur/registres_c';

export default function PageChfRestBreak() {
  return <RegistreGenerique config={registreChfRestBreak} />;
}
