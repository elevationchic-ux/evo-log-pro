'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollTrainingCompletion } from '@/components/portail-collaborateur/registres_c';

export default function PageCollTrainingCompletion() {
  return <RegistreGenerique config={registreCollTrainingCompletion} />;
}
