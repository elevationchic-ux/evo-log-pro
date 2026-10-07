'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclCustomsValuation } from '@/components/portail-declarant/registres_c';

export default function PageDeclCustomsValuation() {
  return <RegistreGenerique config={registreDeclCustomsValuation} />;
}
