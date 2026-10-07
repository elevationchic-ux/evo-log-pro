'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreModuleHealth } from '@/components/dashboard/registres';

export default function PageModuleHealth() {
  return <RegistreGenerique config={registreModuleHealth} />;
}
