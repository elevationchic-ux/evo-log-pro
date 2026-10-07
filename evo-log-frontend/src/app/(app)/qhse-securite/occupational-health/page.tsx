'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHealthVisit } from '@/components/qhse-securite/registres';

export default function PageHealthVisit() {
  return <RegistreGenerique config={registreHealthVisit} />;
}
