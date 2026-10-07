'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreActivityRecord } from '@/components/dashboard/registres';

export default function PageActivityRecord() {
  return <RegistreGenerique config={registreActivityRecord} />;
}
