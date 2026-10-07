'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAirTariff } from '@/components/transport-aerien/registres';

export default function PageAirTariff() {
  return <RegistreGenerique config={registreAirTariff} />;
}
