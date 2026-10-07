'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailShuntingPlan } from '@/components/transport-ferroviaire/registres_b';

export default function PageRailShuntingPlan() {
  return <RegistreGenerique config={registreRailShuntingPlan} />;
}
