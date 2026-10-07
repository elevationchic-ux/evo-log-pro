'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreReefer } from '@/components/chaine-froid/registres';

export default function PageColdChainReefer() {
  return <RegistreGenerique config={registreReefer} />;
}
