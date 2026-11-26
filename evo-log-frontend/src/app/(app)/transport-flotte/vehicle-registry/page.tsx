'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVehicleRegistration } from '@/components/transport-flotte/registres';

export default function PageVehicleRegistration() {
  return <RegistreGenerique config={registreVehicleRegistration} />;
}
