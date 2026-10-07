'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMaintWork } from '@/components/pipeline-oleoduc/registres';

export default function PagePipelineMaintenanceWork() {
  return <RegistreGenerique config={registreMaintWork} />;
}
