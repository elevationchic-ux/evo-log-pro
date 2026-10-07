'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTransportbDispatch } from '@/components/transport-flotte/registres_b';

export default function PageTransportbDispatch() {
  return <RegistreGenerique config={registreTransportbDispatch} />;
}
