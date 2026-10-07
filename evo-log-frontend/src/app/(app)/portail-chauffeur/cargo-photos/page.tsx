'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfCargoPhoto } from '@/components/portail-chauffeur/registres_c';

export default function PageChfCargoPhoto() {
  return <RegistreGenerique config={registreChfCargoPhoto} />;
}
