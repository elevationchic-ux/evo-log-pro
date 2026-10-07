'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2LoadMomentCalc } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2LoadMomentCalc() {
  return <RegistreGenerique config={registreHeavy2LoadMomentCalc} />;
}
