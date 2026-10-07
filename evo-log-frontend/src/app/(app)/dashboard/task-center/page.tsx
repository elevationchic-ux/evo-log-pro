'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreUnifiedTask } from '@/components/dashboard/registres';

export default function PageUnifiedTask() {
  return <RegistreGenerique config={registreUnifiedTask} />;
}
