'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreWasteRecord } from '@/components/qhse-securite/registres';

export default function PageWasteRecord() {
  return <RegistreGenerique config={registreWasteRecord} />;
}
