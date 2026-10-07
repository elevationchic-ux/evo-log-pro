'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSerialNumber } from '@/components/magasin-stock/registres';

export default function PageSerialNumber() {
  return <RegistreGenerique config={registreSerialNumber} />;
}
