'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreIncident } from '@/components/tracabilite/registres';

export default function PageIncidentChainOfCommand() {
  return <RegistreGenerique config={registreIncident} />;
}
