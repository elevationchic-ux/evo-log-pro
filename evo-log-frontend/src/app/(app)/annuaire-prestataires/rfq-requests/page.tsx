'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvRfqRequest } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvRfqRequest() {
  return <RegistreGenerique config={registreProvRfqRequest} />;
}
