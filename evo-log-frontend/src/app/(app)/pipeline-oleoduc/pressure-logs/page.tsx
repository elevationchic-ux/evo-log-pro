'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2PressureLog } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2PressureLog() {
  return <RegistreGenerique config={registrePipe2PressureLog} />;
}
