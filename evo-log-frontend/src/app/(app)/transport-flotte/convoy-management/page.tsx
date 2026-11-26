'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreConvoy } from '@/components/transport-flotte/registres';

export default function PageConvoy() {
  return <RegistreGenerique config={registreConvoy} />;
}
