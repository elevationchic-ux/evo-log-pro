'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraTravelBooking } from '@/components/portail-frais/registres_c';

export default function PageFraTravelBooking() {
  return <RegistreGenerique config={registreFraTravelBooking} />;
}
