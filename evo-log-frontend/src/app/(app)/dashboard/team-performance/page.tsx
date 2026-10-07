'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTeamPerformance } from '@/components/dashboard/registres';

export default function PageTeamPerformance() {
  return <RegistreGenerique config={registreTeamPerformance} />;
}
