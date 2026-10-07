'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollTimesheet } from '@/components/portail-collaborateur/registres_c';

export default function PageCollTimesheet() {
  return <RegistreGenerique config={registreCollTimesheet} />;
}
