'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAccessLog } from '@/components/tracabilite/registres';

export default function PageAccessSecurityLog() {
  return <RegistreGenerique config={registreAccessLog} />;
}
