'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreFluvialSafetyRecord } from '@/components/transport-fluvial/registres';

export default function PageFluvialSafetyRecord() {
  return <RegistreGenerique config={registreFluvialSafetyRecord} />;
}
