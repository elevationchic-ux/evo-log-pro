'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDepreciationSchedule } from '@/components/comptabilite-ohada/registres';

export default function PageDepreciationSchedule() {
  return <RegistreGenerique config={registreDepreciationSchedule} />;
}
