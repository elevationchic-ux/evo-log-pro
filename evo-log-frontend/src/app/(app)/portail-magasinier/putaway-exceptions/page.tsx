'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcPutawayException } from '@/components/portail-magasinier/registres_c';

export default function PageMagcPutawayException() {
  return <RegistreGenerique config={registreMagcPutawayException} />;
}
