'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSignature } from '@/components/tracabilite/registres';

export default function PageWitnessSignature() {
  return <RegistreGenerique config={registreSignature} />;
}
