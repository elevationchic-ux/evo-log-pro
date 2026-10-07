'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplOrderNode } from '@/components/logistique-3pl/registres_b';

export default function PageTplOrderNode() {
  return <RegistreGenerique config={registreTplOrderNode} />;
}
