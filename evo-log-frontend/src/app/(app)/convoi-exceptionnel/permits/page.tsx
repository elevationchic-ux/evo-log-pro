'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHLPermit } from '@/components/convoi-exceptionnel/registres';

export default function PageHeavyLiftPermit() {
  return <RegistreGenerique config={registreHLPermit} />;
}
