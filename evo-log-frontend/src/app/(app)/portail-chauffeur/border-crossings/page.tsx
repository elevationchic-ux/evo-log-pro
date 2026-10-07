'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfBorderCrossing } from '@/components/portail-chauffeur/registres_c';

export default function PageChfBorderCrossing() {
  return <RegistreGenerique config={registreChfBorderCrossing} />;
}
