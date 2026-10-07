'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDeclCustomsAuditSupport } from '@/components/portail-declarant/registres_c';

export default function PageDeclCustomsAuditSupport() {
  return <RegistreGenerique config={registreDeclCustomsAuditSupport} />;
}
