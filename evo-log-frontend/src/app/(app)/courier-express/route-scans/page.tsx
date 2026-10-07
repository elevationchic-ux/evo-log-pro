'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCour2RouteScan } from '@/components/courier-express/registres_e';

export default function PageCour2RouteScan() {
  return <RegistreGenerique config={registreCour2RouteScan} />;
}
