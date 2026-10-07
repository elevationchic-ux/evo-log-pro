'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfShiftHandover } from '@/components/portail-chauffeur/registres_c';

export default function PageChfShiftHandover() {
  return <RegistreGenerique config={registreChfShiftHandover} />;
}
