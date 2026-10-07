'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreMagcEquipmentCheck } from '@/components/portail-magasinier/registres_c';

export default function PageMagcEquipmentCheck() {
  return <RegistreGenerique config={registreMagcEquipmentCheck} />;
}
