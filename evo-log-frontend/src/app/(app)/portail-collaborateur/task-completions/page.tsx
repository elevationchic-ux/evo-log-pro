'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollTaskCompletion } from '@/components/portail-collaborateur/registres_c';

export default function PageCollTaskCompletion() {
  return <RegistreGenerique config={registreCollTaskCompletion} />;
}
