'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplReturnAuthorization } from '@/components/logistique-3pl/registres_b';

export default function PageTplReturnAuthorization() {
  return <RegistreGenerique config={registreTplReturnAuthorization} />;
}
