'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvCertification } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvCertification() {
  return <RegistreGenerique config={registreProvCertification} />;
}
