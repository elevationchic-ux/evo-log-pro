'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvision } from '@/components/comptabilite-ohada/registres';

export default function PageProvision() {
  return <RegistreGenerique config={registreProvision} />;
}
