'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpJobPosting } from '@/components/chef-personnel/registres_c';

export default function PageChpJobPosting() {
  return <RegistreGenerique config={registreChpJobPosting} />;
}
