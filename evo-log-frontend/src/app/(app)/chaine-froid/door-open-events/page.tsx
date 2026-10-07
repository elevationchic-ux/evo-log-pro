'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCold2DoorOpenEvent } from '@/components/chaine-froid/registres_e';

export default function PageCold2DoorOpenEvent() {
  return <RegistreGenerique config={registreCold2DoorOpenEvent} />;
}
