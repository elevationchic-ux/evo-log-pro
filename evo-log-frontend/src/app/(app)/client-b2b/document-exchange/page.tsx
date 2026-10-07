'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreB2bDocument } from '@/components/client-b2b/registres';

export default function PageB2bDocument() {
  return <RegistreGenerique config={registreB2bDocument} />;
}
