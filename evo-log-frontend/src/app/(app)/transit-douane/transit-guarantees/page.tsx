'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTransitGuarantee } from '@/components/transit-douane/registres';

export default function PageTransitGuarantee() {
  return <RegistreGenerique config={registreTransitGuarantee} />;
}
