'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePettyCashBox } from '@/components/finance-ohada/registres';

export default function PagePettyCashBox() {
  return <RegistreGenerique config={registrePettyCashBox} />;
}
