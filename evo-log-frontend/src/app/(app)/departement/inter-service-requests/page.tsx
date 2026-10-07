'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreDepServiceRequest } from '@/components/departement/registres_d5';

export default function PageDepServiceRequest() {
  return <RegistreGenerique config={registreDepServiceRequest} />;
}
