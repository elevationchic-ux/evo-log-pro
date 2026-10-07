'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreStevedoringCrew } from '@/components/port-operations/registres';

export default function PageStevedoringCrew() {
  return <RegistreGenerique config={registreStevedoringCrew} />;
}
