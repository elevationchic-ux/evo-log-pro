'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQhseNearMiss } from '@/components/qhse-securite/registres_b';

export default function PageQhseNearMiss() {
  return <RegistreGenerique config={registreQhseNearMiss} />;
}
