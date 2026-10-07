'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAirportCargoWarehouse } from '@/components/transport-aerien/registres';

export default function PageAirportCargoWarehouse() {
  return <RegistreGenerique config={registreAirportCargoWarehouse} />;
}
