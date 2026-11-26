'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCheckpointControl } from '@/components/transport-flotte/registres';

export default function PageCheckpointControl() {
  return <RegistreGenerique config={registreCheckpointControl} />;
}
