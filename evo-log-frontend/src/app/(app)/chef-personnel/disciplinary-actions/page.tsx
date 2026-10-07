'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChpDisciplinaryAction } from '@/components/chef-personnel/registres_c';

export default function PageChpDisciplinaryAction() {
  return <RegistreGenerique config={registreChpDisciplinaryAction} />;
}
