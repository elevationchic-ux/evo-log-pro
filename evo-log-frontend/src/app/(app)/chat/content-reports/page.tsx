'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChtContentReport } from '@/components/chat/registres_d5';

export default function PageChtContentReport() {
  return <RegistreGenerique config={registreChtContentReport} />;
}
