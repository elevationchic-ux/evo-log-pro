'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclPreClearance } from '@/components/portail-declarant/registres_c';

export default function PageDeclPreClearance() {
  return <RegistreGenerique config={registreDeclPreClearance} />;
}
