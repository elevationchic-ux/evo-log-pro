'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePortbVesselTrafficLog } from '@/components/port-operations/registres_b';

export default function PagePortbVesselTrafficLog() {
  return <RegistreGenerique config={registrePortbVesselTrafficLog} />;
}
