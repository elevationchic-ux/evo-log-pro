'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLTrailer } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftModularTrailer() {
  return <RegistreGenerique config={registreHLTrailer} />;
}
