'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLubrication } from '@/components/maintenance-industrielle/registres';

export default function PageLubricationSchedule() {
  return <RegistreGenerique config={registreLubrication} />;
}
