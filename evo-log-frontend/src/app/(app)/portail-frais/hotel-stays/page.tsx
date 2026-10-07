'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFraHotelStay } from '@/components/portail-frais/registres_c';

export default function PageFraHotelStay() {
  return <RegistreGenerique config={registreFraHotelStay} />;
}
