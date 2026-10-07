'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollIncidentReport } from '@/components/portail-collaborateur/registres_c';

export default function PageCollIncidentReport() {
  return <RegistreGenerique config={registreCollIncidentReport} />;
}
