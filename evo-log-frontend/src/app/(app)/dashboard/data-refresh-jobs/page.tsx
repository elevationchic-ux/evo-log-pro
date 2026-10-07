'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDashboardbRefreshJob } from '@/components/dashboard/registres_b';

export default function PageDashboardbRefreshJob() {
  return <RegistreGenerique config={registreDashboardbRefreshJob} />;
}
