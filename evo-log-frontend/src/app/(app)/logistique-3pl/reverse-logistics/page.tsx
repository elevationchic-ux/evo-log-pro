'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplReverseOperation } from '@/components/logistique-3pl/registres';

export default function PageTplReverseOperation() {
  return <RegistreGenerique config={registreTplReverseOperation} />;
}
