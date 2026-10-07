'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTaxDeclaration } from '@/components/comptabilite-ohada/registres';

export default function PageTaxDeclaration() {
  return <RegistreGenerique config={registreTaxDeclaration} />;
}
