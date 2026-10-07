'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQuickAction } from '@/components/dashboard/registres';

export default function PageQuickAction() {
  return <RegistreGenerique config={registreQuickAction} />;
}
