'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplSubProvider } from '@/components/logistique-3pl/registres';

export default function PageTplSubProvider() {
  return <RegistreGenerique config={registreTplSubProvider} />;
}
