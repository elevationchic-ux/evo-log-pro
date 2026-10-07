'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplDamageClaim } from '@/components/logistique-3pl/registres_b';

export default function PageTplDamageClaim() {
  return <RegistreGenerique config={registreTplDamageClaim} />;
}
