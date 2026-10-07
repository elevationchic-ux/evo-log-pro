'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvAvailabilityCalendar } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvAvailabilityCalendar() {
  return <RegistreGenerique config={registreProvAvailabilityCalendar} />;
}
