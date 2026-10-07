'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollFeedback } from '@/components/portail-collaborateur/registres_c';

export default function PageCollFeedback() {
  return <RegistreGenerique config={registreCollFeedback} />;
}
