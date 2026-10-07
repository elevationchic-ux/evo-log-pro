'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspFirstAidLog } from '@/components/portail-qhse/registres_c';

export default function PageQspFirstAidLog() {
  return <RegistreGenerique config={registreQspFirstAidLog} />;
}
