'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2PumpStationRead } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2PumpStationRead() {
  return <RegistreGenerique config={registrePipe2PumpStationRead} />;
}
