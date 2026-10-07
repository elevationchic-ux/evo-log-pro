'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialConvoy } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialConvoy() {
  return <RegistreGenerique config={registreFluvialConvoy} />;
}
