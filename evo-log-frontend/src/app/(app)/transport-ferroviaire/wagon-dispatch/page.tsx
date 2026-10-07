'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailWagonDispatch } from '@/components/transport-ferroviaire/registres_b';

export default function PageRailWagonDispatch() {
  return <RegistreGenerique config={registreRailWagonDispatch} />;
}
