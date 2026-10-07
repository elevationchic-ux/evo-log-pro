'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePilotageSession } from '@/components/port-operations/registres';

export default function PagePilotageSession() {
  return <RegistreGenerique config={registrePilotageSession} />;
}
