'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialPortFee } from '@/components/transport-fluvial/registres_b';

export default function PageFluvialPortFee() {
  return <RegistreGenerique config={registreFluvialPortFee} />;
}
