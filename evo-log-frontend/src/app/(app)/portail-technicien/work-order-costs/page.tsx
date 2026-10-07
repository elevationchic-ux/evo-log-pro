'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechWorkOrderCost } from '@/components/portail-technicien/registres_c';

export default function PageTechWorkOrderCost() {
  return <RegistreGenerique config={registreTechWorkOrderCost} />;
}
