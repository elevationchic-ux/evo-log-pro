'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreEnergyMeter } from '@/components/chaine-froid/registres';

export default function PageColdChainEnergyMeter() {
  return <RegistreGenerique config={registreEnergyMeter} />;
}
