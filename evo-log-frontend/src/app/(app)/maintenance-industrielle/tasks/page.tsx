'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTask } from '@/components/maintenance-industrielle/registres';

export default function PageMaintenanceTask() {
  return <RegistreGenerique config={registreTask} />;
}
