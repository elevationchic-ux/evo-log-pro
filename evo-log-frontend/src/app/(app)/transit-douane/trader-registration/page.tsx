'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTraderRegistration } from '@/components/transit-douane/registres';

export default function PageTraderRegistration() {
  return <RegistreGenerique config={registreTraderRegistration} />;
}
