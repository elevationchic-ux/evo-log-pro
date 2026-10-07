'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialCrewRoster } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialCrewRoster() {
  return <RegistreGenerique config={registreFluvialCrewRoster} />;
}
