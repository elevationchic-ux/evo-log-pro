'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHaccp } from '@/components/chaine-froid/registres';

export default function PageColdChainHaccpRecord() {
  return <RegistreGenerique config={registreHaccp} />;
}
