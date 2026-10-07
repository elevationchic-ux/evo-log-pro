'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVehicleLifecycle } from '@/components/parc-vehicules/registres';

export default function PageVehicleLifecycle() {
  return <RegistreGenerique config={registreVehicleLifecycle} />;
}
