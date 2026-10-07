'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2SpillResponseAction } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2SpillResponseAction() {
  return <RegistreGenerique config={registrePipe2SpillResponseAction} />;
}
