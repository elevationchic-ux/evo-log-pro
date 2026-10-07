'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreComplianceRecord } from '@/components/qhse-securite/registres';

export default function PageComplianceRecord() {
  return <RegistreGenerique config={registreComplianceRecord} />;
}
