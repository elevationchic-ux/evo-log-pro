'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommQuote } from '@/components/portail-commercial/registres_c';

export default function PageCommQuote() {
  return <RegistreGenerique config={registreCommQuote} />;
}
