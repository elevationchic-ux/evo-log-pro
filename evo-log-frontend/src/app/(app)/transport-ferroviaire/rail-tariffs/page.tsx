'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailTariff } from '@/components/transport-ferroviaire/registres';

export default function PageRailTariff() {
  return <RegistreGenerique config={registreRailTariff} />;
}
