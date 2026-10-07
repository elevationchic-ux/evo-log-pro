'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraOfficeSupply } from '@/components/portail-frais/registres_c';

export default function PageFraOfficeSupply() {
  return <RegistreGenerique config={registreFraOfficeSupply} />;
}
