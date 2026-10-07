'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2ConvoyStagingReport } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2ConvoyStagingReport() {
  return <RegistreGenerique config={registreHeavy2ConvoyStagingReport} />;
}
