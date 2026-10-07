'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2IntegrityAssessment } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2IntegrityAssessment() {
  return <RegistreGenerique config={registrePipe2IntegrityAssessment} />;
}
