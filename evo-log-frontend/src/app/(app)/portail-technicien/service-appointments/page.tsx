'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechServiceAppointment } from '@/components/portail-technicien/registres_c';

export default function PageTechServiceAppointment() {
  return <RegistreGenerique config={registreTechServiceAppointment} />;
}
