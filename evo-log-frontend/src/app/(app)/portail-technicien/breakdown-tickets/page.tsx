'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechBreakdownTicket } from '@/components/portail-technicien/registres_c';

export default function PageTechBreakdownTicket() {
  return <RegistreGenerique config={registreTechBreakdownTicket} />;
}
