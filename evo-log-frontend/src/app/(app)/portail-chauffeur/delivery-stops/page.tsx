'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfDeliveryStop } from '@/components/portail-chauffeur/registres_c';

export default function PageChfDeliveryStop() {
  return <RegistreGenerique config={registreChfDeliveryStop} />;
}
