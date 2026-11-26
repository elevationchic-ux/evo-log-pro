'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCustomsRegime } from '@/components/transit-douane/registres';

export default function PageCustomsRegime() {
  return <RegistreGenerique config={registreCustomsRegime} />;
}
