'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCour2LastMileHandoff } from '@/components/courier-express/registres_e';

export default function PageCour2LastMileHandoff() {
  return <RegistreGenerique config={registreCour2LastMileHandoff} />;
}
