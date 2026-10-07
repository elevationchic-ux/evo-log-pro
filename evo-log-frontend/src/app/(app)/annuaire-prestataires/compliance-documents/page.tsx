'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreProvComplianceDoc } from '@/components/annuaire-prestataires/registres_c';

export default function PageProvComplianceDoc() {
  return <RegistreGenerique config={registreProvComplianceDoc} />;
}
