'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollQualityCheck } from '@/components/portail-collaborateur/registres_c';

export default function PageCollQualityCheck() {
  return <RegistreGenerique config={registreCollQualityCheck} />;
}
