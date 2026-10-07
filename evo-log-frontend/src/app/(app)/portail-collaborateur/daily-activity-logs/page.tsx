'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollActivityLog } from '@/components/portail-collaborateur/registres_c';

export default function PageCollActivityLog() {
  return <RegistreGenerique config={registreCollActivityLog} />;
}
