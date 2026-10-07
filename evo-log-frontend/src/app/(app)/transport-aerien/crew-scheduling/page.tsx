'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCrewRoster } from '@/components/transport-aerien/registres';

export default function PageCrewRoster() {
  return <RegistreGenerique config={registreCrewRoster} />;
}
