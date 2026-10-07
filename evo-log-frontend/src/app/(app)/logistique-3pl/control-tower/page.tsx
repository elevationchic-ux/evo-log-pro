'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplControlTower } from '@/components/logistique-3pl/registres';

export default function PageTplControlTower() {
  return <RegistreGenerique config={registreTplControlTower} />;
}
