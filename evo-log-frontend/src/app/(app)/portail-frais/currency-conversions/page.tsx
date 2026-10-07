'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraCurrencyConversion } from '@/components/portail-frais/registres_c';

export default function PageFraCurrencyConversion() {
  return <RegistreGenerique config={registreFraCurrencyConversion} />;
}
