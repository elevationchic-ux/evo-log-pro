'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfFuelLog } from '@/components/portail-chauffeur/registres_c';

export default function PageChfFuelLog() {
  return <RegistreGenerique config={registreChfFuelLog} />;
}
