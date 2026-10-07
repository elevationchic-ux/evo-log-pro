'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTariffReference } from '@/components/transit-douane/registres';

export default function PageTariffReference() {
  return <RegistreGenerique config={registreTariffReference} />;
}
