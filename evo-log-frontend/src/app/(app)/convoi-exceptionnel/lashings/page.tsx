'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLLashing } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftLashing() {
  return <RegistreGenerique config={registreHLLashing} />;
}
