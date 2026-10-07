'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHsClassification } from '@/components/transit-douane/registres';

export default function PageHsClassification() {
  return <RegistreGenerique config={registreHsClassification} />;
}
