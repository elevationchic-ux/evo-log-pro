'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailTrainPath } from '@/components/transport-ferroviaire/registres';

export default function PageRailTrainPath() {
  return <RegistreGenerique config={registreRailTrainPath} />;
}
