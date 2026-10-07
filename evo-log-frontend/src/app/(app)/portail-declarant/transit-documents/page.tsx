'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclTransitDocument } from '@/components/portail-declarant/registres_c';

export default function PageDeclTransitDocument() {
  return <RegistreGenerique config={registreDeclTransitDocument} />;
}
