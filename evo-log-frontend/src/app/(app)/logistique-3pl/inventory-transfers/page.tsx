'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTplInventoryTransfer } from '@/components/logistique-3pl/registres_b';

export default function PageTplInventoryTransfer() {
  return <RegistreGenerique config={registreTplInventoryTransfer} />;
}
