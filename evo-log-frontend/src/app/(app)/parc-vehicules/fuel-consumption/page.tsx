'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFuelConsumption } from '@/components/parc-vehicules/registres';

export default function PageFuelConsumption() {
  return <RegistreGenerique config={registreFuelConsumption} />;
}
