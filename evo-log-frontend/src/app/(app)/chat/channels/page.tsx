'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreChtChannel } from '@/components/chat/registres_d5';

export default function PageChtChannel() {
  return <RegistreGenerique config={registreChtChannel} />;
}
