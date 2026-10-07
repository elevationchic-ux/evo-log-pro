'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreGpsDevice } from '@/components/transport-flotte/registres';

export default function PageGpsDevice() {
  return <RegistreGenerique config={registreGpsDevice} />;
}
