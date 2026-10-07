'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreParcLeaseContract } from '@/components/parc-vehicules/registres_b';

export default function PageParcLeaseContract() {
  return <RegistreGenerique config={registreParcLeaseContract} />;
}
