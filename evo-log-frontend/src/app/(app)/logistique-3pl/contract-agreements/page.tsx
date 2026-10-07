'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplContract } from '@/components/logistique-3pl/registres';

export default function PageTplContract() {
  return <RegistreGenerique config={registreTplContract} />;
}
