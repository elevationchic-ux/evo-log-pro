'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollAvailability } from '@/components/portail-collaborateur/registres_c';

export default function PageCollAvailability() {
  return <RegistreGenerique config={registreCollAvailability} />;
}
