'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCour2ExceptionParcel } from '@/components/courier-express/registres_e';

export default function PageCour2ExceptionParcel() {
  return <RegistreGenerique config={registreCour2ExceptionParcel} />;
}
