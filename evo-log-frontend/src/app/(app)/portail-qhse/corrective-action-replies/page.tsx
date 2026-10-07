'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspCapaReply } from '@/components/portail-qhse/registres_c';

export default function PageQspCapaReply() {
  return <RegistreGenerique config={registreQspCapaReply} />;
}
