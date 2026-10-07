'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreBunkeringOrder } from '@/components/port-operations/registres';

export default function PageBunkeringOrder() {
  return <RegistreGenerique config={registreBunkeringOrder} />;
}
