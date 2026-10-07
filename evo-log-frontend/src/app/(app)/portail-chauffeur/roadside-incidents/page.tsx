'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfRoadsideIncident } from '@/components/portail-chauffeur/registres_c';

export default function PageChfRoadsideIncident() {
  return <RegistreGenerique config={registreChfRoadsideIncident} />;
}
