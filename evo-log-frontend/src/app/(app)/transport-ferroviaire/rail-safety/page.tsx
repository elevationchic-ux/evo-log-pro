'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRailSafetyRecord } from '@/components/transport-ferroviaire/registres';

export default function PageRailSafetyRecord() {
  return <RegistreGenerique config={registreRailSafetyRecord} />;
}
