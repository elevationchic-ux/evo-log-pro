'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2InterfaceDetection } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2InterfaceDetection() {
  return <RegistreGenerique config={registrePipe2InterfaceDetection} />;
}
