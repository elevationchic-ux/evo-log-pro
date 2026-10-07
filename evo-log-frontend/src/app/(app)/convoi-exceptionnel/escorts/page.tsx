'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLEscort } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftEscort() {
  return <RegistreGenerique config={registreHLEscort} />;
}
