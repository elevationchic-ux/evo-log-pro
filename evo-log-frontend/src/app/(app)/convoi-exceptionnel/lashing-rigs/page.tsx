'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2LashingRig } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2LashingRig() {
  return <RegistreGenerique config={registreHeavy2LashingRig} />;
}
