'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCommCompetitorNote } from '@/components/portail-commercial/registres_d';

export default function PageCommCompetitorNote() {
  return <RegistreGenerique config={registreCommCompetitorNote} />;
}
