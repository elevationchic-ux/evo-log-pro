'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspMsdsAck } from '@/components/portail-qhse/registres_c';

export default function PageQspMsdsAck() {
  return <RegistreGenerique config={registreQspMsdsAck} />;
}
