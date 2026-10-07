'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2PermitObtention } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2PermitObtention() {
  return <RegistreGenerique config={registreHeavy2PermitObtention} />;
}
