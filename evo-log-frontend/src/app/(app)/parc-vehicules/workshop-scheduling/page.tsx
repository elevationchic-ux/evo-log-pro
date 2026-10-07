'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWorkshopAppointment } from '@/components/parc-vehicules/registres';

export default function PageWorkshopAppointment() {
  return <RegistreGenerique config={registreWorkshopAppointment} />;
}
