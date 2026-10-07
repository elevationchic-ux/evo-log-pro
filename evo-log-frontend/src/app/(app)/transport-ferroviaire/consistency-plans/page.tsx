'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailConsistencyPlan } from '@/components/transport-ferroviaire/registres';

export default function PageRailConsistencyPlan() {
  return <RegistreGenerique config={registreRailConsistencyPlan} />;
}
