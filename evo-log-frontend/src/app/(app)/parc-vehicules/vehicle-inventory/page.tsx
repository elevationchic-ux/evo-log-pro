'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVehicleInventory } from '@/components/parc-vehicules/registres';

export default function PageVehicleInventory() {
  return <RegistreGenerique config={registreVehicleInventory} />;
}
