'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfMileageLog } from '@/components/portail-chauffeur/registres_c';

export default function PageChfMileageLog() {
  return <RegistreGenerique config={registreChfMileageLog} />;
}
