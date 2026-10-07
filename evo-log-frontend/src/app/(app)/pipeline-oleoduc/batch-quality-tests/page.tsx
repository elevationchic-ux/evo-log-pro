'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePipe2BatchQualityTest } from '@/components/pipeline-oleoduc/registres_e';

export default function PagePipe2BatchQualityTest() {
  return <RegistreGenerique config={registrePipe2BatchQualityTest} />;
}
