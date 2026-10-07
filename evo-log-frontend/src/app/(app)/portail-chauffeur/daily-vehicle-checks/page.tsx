'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfDailyVehicleCheck } from '@/components/portail-chauffeur/registres_c';

export default function PageChfDailyVehicleCheck() {
  return <RegistreGenerique config={registreChfDailyVehicleCheck} />;
}
