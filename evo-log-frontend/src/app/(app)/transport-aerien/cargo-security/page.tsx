'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCargoSecurityScreen } from '@/components/transport-aerien/registres';

export default function PageCargoSecurityScreen() {
  return <RegistreGenerique config={registreCargoSecurityScreen} />;
}
