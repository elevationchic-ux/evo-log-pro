'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplDockAppointment } from '@/components/logistique-3pl/registres_b';

export default function PageTplDockAppointment() {
  return <RegistreGenerique config={registreTplDockAppointment} />;
}
