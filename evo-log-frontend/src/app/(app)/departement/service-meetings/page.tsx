'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDepServiceMeeting } from '@/components/departement/registres_d5';

export default function PageDepServiceMeeting() {
  return <RegistreGenerique config={registreDepServiceMeeting} />;
}
