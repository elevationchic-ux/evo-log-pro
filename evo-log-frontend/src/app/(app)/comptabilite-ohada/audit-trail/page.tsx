'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAuditPaf } from '@/components/comptabilite-ohada/registres';

export default function PageAuditPaf() {
  return <RegistreGenerique config={registreAuditPaf} />;
}
