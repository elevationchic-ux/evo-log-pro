'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialBallastOperation } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialBallastOperation() {
  return <RegistreGenerique config={registreFluvialBallastOperation} />;
}
