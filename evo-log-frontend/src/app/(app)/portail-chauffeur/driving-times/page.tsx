'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfDrivingTimeRecord } from '@/components/portail-chauffeur/registres_c';

export default function PageChfDrivingTimeRecord() {
  return <RegistreGenerique config={registreChfDrivingTimeRecord} />;
}
