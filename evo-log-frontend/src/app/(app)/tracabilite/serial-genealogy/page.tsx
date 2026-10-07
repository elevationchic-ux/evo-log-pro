'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSerialGenealogy } from '@/components/tracabilite/registres';

export default function PageSerialGenealogy() {
  return <RegistreGenerique config={registreSerialGenealogy} />;
}
