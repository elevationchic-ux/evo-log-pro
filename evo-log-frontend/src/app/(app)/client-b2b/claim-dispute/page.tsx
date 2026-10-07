'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreClientClaim } from '@/components/client-b2b/registres';

export default function PageClientClaim() {
  return <RegistreGenerique config={registreClientClaim} />;
}
