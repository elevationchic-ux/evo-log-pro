'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAccountReport } from '@/components/client-b2b/registres';

export default function PageAccountReport() {
  return <RegistreGenerique config={registreAccountReport} />;
}
