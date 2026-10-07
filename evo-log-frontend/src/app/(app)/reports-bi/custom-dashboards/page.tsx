'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCustomDashboard } from '@/components/reports-bi/registres';

export default function PageCustomDashboard() {
  return <RegistreGenerique config={registreCustomDashboard} />;
}
