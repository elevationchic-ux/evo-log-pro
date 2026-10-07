'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpOrgMovement } from '@/components/chef-personnel/registres_c';

export default function PageChpOrgMovement() {
  return <RegistreGenerique config={registreChpOrgMovement} />;
}
