'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreB2bContract } from '@/components/client-b2b/registres';

export default function PageB2bContract() {
  return <RegistreGenerique config={registreB2bContract} />;
}
