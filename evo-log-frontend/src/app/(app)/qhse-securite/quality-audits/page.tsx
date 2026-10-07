'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQualityAudit } from '@/components/qhse-securite/registres';

export default function PageQualityAudit() {
  return <RegistreGenerique config={registreQualityAudit} />;
}
