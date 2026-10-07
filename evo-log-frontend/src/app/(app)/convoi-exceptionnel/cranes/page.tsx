'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLCrane } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftCrane() {
  return <RegistreGenerique config={registreHLCrane} />;
}
