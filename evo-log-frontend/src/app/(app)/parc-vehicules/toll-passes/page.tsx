'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreParcTollPass } from '@/components/parc-vehicules/registres_b';

export default function PageParcTollPass() {
  return <RegistreGenerique config={registreParcTollPass} />;
}
