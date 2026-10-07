'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2FlowCalibration } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2FlowCalibration() {
  return <RegistreGenerique config={registrePipe2FlowCalibration} />;
}
