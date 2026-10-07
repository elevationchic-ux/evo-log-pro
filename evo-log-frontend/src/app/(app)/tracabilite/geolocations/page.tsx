'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreGeolocation } from '@/components/tracabilite/registres';

export default function PageGeolocationTrace() {
  return <RegistreGenerique config={registreGeolocation} />;
}
