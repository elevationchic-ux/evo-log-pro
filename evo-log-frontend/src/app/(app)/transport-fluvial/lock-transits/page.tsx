'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreLockTransit } from '@/components/transport-fluvial/registres';

export default function PageLockTransit() {
  return <RegistreGenerique config={registreLockTransit} />;
}
