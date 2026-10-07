'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSku } from '@/components/chaine-froid/registres';

export default function PageColdChainProduct() {
  return <RegistreGenerique config={registreSku} />;
}
