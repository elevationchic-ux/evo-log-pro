'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSla } from '@/components/courier-express/registres';

export default function PageCourierSla() {
  return <RegistreGenerique config={registreSla} />;
}
