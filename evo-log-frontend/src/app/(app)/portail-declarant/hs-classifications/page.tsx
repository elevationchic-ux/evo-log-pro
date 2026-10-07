'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclHsClassification } from '@/components/portail-declarant/registres_c';

export default function PageDeclHsClassification() {
  return <RegistreGenerique config={registreDeclHsClassification} />;
}
