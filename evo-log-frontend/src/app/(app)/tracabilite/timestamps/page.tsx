'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTimestamp } from '@/components/tracabilite/registres';

export default function PageTimestampAuthority() {
  return <RegistreGenerique config={registreTimestamp} />;
}
