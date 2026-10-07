'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCargoHandoff } from '@/components/tracabilite/registres';

export default function PageCargoHandoff() {
  return <RegistreGenerique config={registreCargoHandoff} />;
}
