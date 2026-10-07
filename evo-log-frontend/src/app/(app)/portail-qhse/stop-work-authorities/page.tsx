'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspStopWorkAuthority } from '@/components/portail-qhse/registres_c';

export default function PageQspStopWorkAuthority() {
  return <RegistreGenerique config={registreQspStopWorkAuthority} />;
}
