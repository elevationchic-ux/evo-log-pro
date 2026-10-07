'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplWarehouse } from '@/components/logistique-3pl/registres';

export default function PageTplWarehouse() {
  return <RegistreGenerique config={registreTplWarehouse} />;
}
