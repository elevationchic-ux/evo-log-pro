'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspWorkPermitRequest } from '@/components/portail-qhse/registres_c';

export default function PageQspWorkPermitRequest() {
  return <RegistreGenerique config={registreQspWorkPermitRequest} />;
}
