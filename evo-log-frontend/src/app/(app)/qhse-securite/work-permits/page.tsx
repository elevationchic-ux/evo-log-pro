'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQhseWorkPermit } from '@/components/qhse-securite/registres_b';

export default function PageQhseWorkPermit() {
  return <RegistreGenerique config={registreQhseWorkPermit} />;
}
