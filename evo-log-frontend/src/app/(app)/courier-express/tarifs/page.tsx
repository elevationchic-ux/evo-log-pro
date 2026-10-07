'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTarifEx } from '@/components/courier-express/registres';

export default function PageCourierTarif() {
  return <RegistreGenerique config={registreTarifEx} />;
}
