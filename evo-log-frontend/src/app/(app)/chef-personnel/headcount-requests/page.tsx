'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpHeadcountRequest } from '@/components/chef-personnel/registres_c';

export default function PageChpHeadcountRequest() {
  return <RegistreGenerique config={registreChpHeadcountRequest} />;
}
