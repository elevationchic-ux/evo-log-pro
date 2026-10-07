'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePressureReading } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelinePressureReading() {
  return <RegistreGenerique config={registrePressureReading} />;
}
