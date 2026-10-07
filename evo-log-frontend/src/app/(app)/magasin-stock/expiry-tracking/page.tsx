'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreExpiryRecord } from '@/components/magasin-stock/registres';

export default function PageExpiryRecord() {
  return <RegistreGenerique config={registreExpiryRecord} />;
}
