'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTraceEvent } from '@/components/tracabilite/registres';

export default function PageTraceabilityEvent() {
  return <RegistreGenerique config={registreTraceEvent} />;
}
