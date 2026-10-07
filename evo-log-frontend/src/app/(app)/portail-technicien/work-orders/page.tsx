'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechWorkOrder } from '@/components/portail-technicien/registres_c';

export default function PageTechWorkOrder() {
  return <RegistreGenerique config={registreTechWorkOrder} />;
}
