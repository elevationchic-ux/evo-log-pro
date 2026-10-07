'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCour2ReturnToSender } from '@/components/courier-express/registres_e';

export default function PageCour2ReturnToSender() {
  return <RegistreGenerique config={registreCour2ReturnToSender} />;
}
