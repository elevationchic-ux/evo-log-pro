'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollExpenseDeclaration } from '@/components/portail-collaborateur/registres_c';

export default function PageCollExpenseDeclaration() {
  return <RegistreGenerique config={registreCollExpenseDeclaration} />;
}
