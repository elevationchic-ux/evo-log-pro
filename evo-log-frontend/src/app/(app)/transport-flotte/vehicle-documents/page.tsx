'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVehicleDocument } from '@/components/transport-flotte/registres';

export default function PageVehicleDocument() {
  return <RegistreGenerique config={registreVehicleDocument} />;
}
