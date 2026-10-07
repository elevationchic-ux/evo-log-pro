'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLiveAnimalShipment } from '@/components/transport-aerien/registres_b';

export default function PageLiveAnimalShipment() {
  return <RegistreGenerique config={registreLiveAnimalShipment} />;
}
