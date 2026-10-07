'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDisciplinaryCase } from '@/components/rh-personnel/registres';

export default function PageDisciplinaryCase() {
  return <RegistreGenerique config={registreDisciplinaryCase} />;
}
