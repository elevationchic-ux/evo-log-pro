'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePhysicalInspection } from '@/components/transit-douane/registres';

export default function PagePhysicalInspection() {
  return <RegistreGenerique config={registrePhysicalInspection} />;
}
