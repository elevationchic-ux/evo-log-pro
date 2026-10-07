'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfTripSheet } from '@/components/portail-chauffeur/registres_c';

export default function PageChfTripSheet() {
  return <RegistreGenerique config={registreChfTripSheet} />;
}
