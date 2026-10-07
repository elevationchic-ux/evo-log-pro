'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDashboardbOperationalKpi } from '@/components/dashboard/registres_b';

export default function PageDashboardbOperationalKpi() {
  return <RegistreGenerique config={registreDashboardbOperationalKpi} />;
}
