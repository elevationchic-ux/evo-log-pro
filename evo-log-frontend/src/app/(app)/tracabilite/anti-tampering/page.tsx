'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreAntiTampering } from '@/components/tracabilite/registres';

export default function PageAntiTamperingEvent() {
  return <RegistreGenerique config={registreAntiTampering} />;
}
