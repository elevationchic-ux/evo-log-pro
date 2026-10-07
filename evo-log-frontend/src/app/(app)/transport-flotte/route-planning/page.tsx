'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRoutePlan } from '@/components/transport-flotte/registres';

export default function PageRoutePlan() {
  return <RegistreGenerique config={registreRoutePlan} />;
}
