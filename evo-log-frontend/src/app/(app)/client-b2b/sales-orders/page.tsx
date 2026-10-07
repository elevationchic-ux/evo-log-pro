'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreB2bCSalesOrder } from '@/components/client-b2b/registres_c';

export default function PageB2bCSalesOrder() {
  return <RegistreGenerique config={registreB2bCSalesOrder} />;
}
