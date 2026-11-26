'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTransitbIncoterm } from '@/components/transit-douane/registres_b';

export default function PageTransitbIncoterm() {
  return <RegistreGenerique config={registreTransitbIncoterm} />;
}
