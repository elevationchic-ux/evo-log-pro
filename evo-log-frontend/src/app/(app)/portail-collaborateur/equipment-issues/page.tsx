'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCollEquipmentIssue } from '@/components/portail-collaborateur/registres_c';

export default function PageCollEquipmentIssue() {
  return <RegistreGenerique config={registreCollEquipmentIssue} />;
}
