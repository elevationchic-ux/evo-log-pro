'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2CorrosionReading } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2CorrosionReading() {
  return <RegistreGenerique config={registrePipe2CorrosionReading} />;
}
