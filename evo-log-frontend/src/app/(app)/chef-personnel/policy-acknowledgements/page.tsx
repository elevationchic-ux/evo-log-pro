'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpPolicyAck } from '@/components/chef-personnel/registres_c';

export default function PageChpPolicyAck() {
  return <RegistreGenerique config={registreChpPolicyAck} />;
}
