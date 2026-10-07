'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreShipmentBooking } from '@/components/client-b2b/registres';

export default function PageShipmentBooking() {
  return <RegistreGenerique config={registreShipmentBooking} />;
}
