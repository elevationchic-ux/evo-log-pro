'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailShuntingYard } from '@/components/transport-ferroviaire/registres';

export default function PageRailShuntingYard() {
  return <RegistreGenerique config={registreRailShuntingYard} />;
}
