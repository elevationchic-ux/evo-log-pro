'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreUnifiedAgenda } from '@/components/dashboard/registres';

export default function PageUnifiedAgenda() {
  return <RegistreGenerique config={registreUnifiedAgenda} />;
}
