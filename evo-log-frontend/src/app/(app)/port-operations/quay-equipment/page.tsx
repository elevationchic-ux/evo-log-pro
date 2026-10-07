'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQuayEquipment } from '@/components/port-operations/registres';

export default function PageQuayEquipment() {
  return <RegistreGenerique config={registreQuayEquipment} />;
}
