'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registrePpeItem } from '@/components/qhse-securite/registres';

export default function PagePpeItem() {
  return <RegistreGenerique config={registrePpeItem} />;
}
