'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreNoiseComplianceRecord } from '@/components/transport-aerien/registres_b';

export default function PageNoiseComplianceRecord() {
  return <RegistreGenerique config={registreNoiseComplianceRecord} />;
}
