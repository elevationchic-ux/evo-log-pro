'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollSiteAccessLog } from '@/components/portail-collaborateur/registres_c';

export default function PageCollSiteAccessLog() {
  return <RegistreGenerique config={registreCollSiteAccessLog} />;
}
