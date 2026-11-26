'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailTrainConsist } from '@/components/transport-ferroviaire/registres_b';

export default function PageRailTrainConsist() {
  return <RegistreGenerique config={registreRailTrainConsist} />;
}
