'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSparePart } from '@/components/parc-vehicules/registres';

export default function PageSparePart() {
  return <RegistreGenerique config={registreSparePart} />;
}
