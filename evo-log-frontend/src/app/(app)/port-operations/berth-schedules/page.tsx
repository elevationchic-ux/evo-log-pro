'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePortbBerthSchedule } from '@/components/port-operations/registres_b';

export default function PagePortbBerthSchedule() {
  return <RegistreGenerique config={registrePortbBerthSchedule} />;
}
