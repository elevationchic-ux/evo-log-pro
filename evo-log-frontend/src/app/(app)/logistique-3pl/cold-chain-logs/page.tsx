'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplColdChainLog } from '@/components/logistique-3pl/registres_b';

export default function PageTplColdChainLog() {
  return <RegistreGenerique config={registreTplColdChainLog} />;
}
