'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollDeliverable } from '@/components/portail-collaborateur/registres_c';

export default function PageCollDeliverable() {
  return <RegistreGenerique config={registreCollDeliverable} />;
}
