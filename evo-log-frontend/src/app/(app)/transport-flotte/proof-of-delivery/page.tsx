'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTransportbPod } from '@/components/transport-flotte/registres_b';

export default function PageTransportbPod() {
  return <RegistreGenerique config={registreTransportbPod} />;
}
