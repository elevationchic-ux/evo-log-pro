'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcPutawayTask } from '@/components/portail-magasinier/registres_c';

export default function PageMagcPutawayTask() {
  return <RegistreGenerique config={registreMagcPutawayTask} />;
}
