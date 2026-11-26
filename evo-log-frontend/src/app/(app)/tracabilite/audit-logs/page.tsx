'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAuditLog } from '@/components/tracabilite/registres';

export default function PageImmutableAuditLog() {
  return <RegistreGenerique config={registreAuditLog} />;
}
