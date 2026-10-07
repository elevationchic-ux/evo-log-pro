'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclCustomsDeclaration } from '@/components/portail-declarant/registres_c';

export default function PageDeclCustomsDeclaration() {
  return <RegistreGenerique config={registreDeclCustomsDeclaration} />;
}
