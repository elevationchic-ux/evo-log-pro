'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCour2CourierShiftLog } from '@/components/courier-express/registres_e';

export default function PageCour2CourierShiftLog() {
  return <RegistreGenerique config={registreCour2CourierShiftLog} />;
}
