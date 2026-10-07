'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDashboardbScorecard } from '@/components/dashboard/registres_b';

export default function PageDashboardbScorecard() {
  return <RegistreGenerique config={registreDashboardbScorecard} />;
}
