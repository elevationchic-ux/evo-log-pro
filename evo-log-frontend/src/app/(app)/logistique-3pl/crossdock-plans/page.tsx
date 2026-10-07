'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplCrossDock } from '@/components/logistique-3pl/registres';

export default function PageTplCrossDock() {
  return <RegistreGenerique config={registreTplCrossDock} />;
}
