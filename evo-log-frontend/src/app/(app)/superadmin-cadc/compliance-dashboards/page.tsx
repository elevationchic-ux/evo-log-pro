'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreComplianceDashboard } from '@/components/superadmin-cadc/registres';

export default function PageComplianceDashboard() {
  return <RegistreGenerique config={registreComplianceDashboard} />;
}
