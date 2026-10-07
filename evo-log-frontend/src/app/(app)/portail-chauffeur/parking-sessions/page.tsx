'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfParkingSession } from '@/components/portail-chauffeur/registres_c';

export default function PageChfParkingSession() {
  return <RegistreGenerique config={registreChfParkingSession} />;
}
