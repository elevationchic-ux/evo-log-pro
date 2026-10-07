'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2EscortSchedule } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2EscortSchedule() {
  return <RegistreGenerique config={registreHeavy2EscortSchedule} />;
}
