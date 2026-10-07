'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplInventoryValuation } from '@/components/logistique-3pl/registres';

export default function PageTplInventoryValuation() {
  return <RegistreGenerique config={registreTplInventoryValuation} />;
}
