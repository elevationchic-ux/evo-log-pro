'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreVaccinBatch } from '@/components/chaine-froid/registres';

export default function PageColdChainVaccinBatch() {
  return <RegistreGenerique config={registreVaccinBatch} />;
}
