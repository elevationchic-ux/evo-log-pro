'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplPickingLine } from '@/components/logistique-3pl/registres';

export default function PageTplPickingLine() {
  return <RegistreGenerique config={registreTplPickingLine} />;
}
