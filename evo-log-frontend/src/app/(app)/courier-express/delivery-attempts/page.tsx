'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCour2DeliveryAttempt } from '@/components/courier-express/registres_e';

export default function PageCour2DeliveryAttempt() {
  return <RegistreGenerique config={registreCour2DeliveryAttempt} />;
}
