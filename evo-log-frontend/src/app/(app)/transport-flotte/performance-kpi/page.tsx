'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFleetKpi } from '@/components/transport-flotte/registres';

export default function PageFleetKpi() {
  return <RegistreGenerique config={registreFleetKpi} />;
}
