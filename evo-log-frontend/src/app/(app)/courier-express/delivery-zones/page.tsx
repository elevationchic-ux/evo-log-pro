'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeliveryZone } from '@/components/courier-express/registres';

export default function PageCourierDeliveryZone() {
  return <RegistreGenerique config={registreDeliveryZone} />;
}
