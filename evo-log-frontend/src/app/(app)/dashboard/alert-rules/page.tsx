'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDashboardbAlertRule } from '@/components/dashboard/registres_b';

export default function PageDashboardbAlertRule() {
  return <RegistreGenerique config={registreDashboardbAlertRule} />;
}
