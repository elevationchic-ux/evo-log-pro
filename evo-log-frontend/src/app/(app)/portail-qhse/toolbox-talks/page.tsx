'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspToolboxTalk } from '@/components/portail-qhse/registres_c';

export default function PageQspToolboxTalk() {
  return <RegistreGenerique config={registreQspToolboxTalk} />;
}
