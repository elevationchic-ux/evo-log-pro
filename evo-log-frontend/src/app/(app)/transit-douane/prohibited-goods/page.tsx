'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProhibitedGood } from '@/components/transit-douane/registres';

export default function PageProhibitedGood() {
  return <RegistreGenerique config={registreProhibitedGood} />;
}
