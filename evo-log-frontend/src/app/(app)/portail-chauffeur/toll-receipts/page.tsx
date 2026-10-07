'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChfTollReceipt } from '@/components/portail-chauffeur/registres_c';

export default function PageChfTollReceipt() {
  return <RegistreGenerique config={registreChfTollReceipt} />;
}
