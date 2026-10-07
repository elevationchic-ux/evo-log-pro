'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAnalyticalSection } from '@/components/comptabilite-ohada/registres';

export default function PageAnalyticalSection() {
  return <RegistreGenerique config={registreAnalyticalSection} />;
}
