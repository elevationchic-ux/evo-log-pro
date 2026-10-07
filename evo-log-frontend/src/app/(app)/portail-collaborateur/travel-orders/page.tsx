'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollTravelOrder } from '@/components/portail-collaborateur/registres_c';

export default function PageCollTravelOrder() {
  return <RegistreGenerique config={registreCollTravelOrder} />;
}
