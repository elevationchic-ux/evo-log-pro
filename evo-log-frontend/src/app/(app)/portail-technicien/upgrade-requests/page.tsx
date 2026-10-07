'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechUpgradeRequest } from '@/components/portail-technicien/registres_c';

export default function PageTechUpgradeRequest() {
  return <RegistreGenerique config={registreTechUpgradeRequest} />;
}
