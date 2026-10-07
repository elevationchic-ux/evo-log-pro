'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDashboardbSavedView } from '@/components/dashboard/registres_b';

export default function PageDashboardbSavedView() {
  return <RegistreGenerique config={registreDashboardbSavedView} />;
}
