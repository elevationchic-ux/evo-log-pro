'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLRigging } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftRiggingMethod() {
  return <RegistreGenerique config={registreHLRigging} />;
}
