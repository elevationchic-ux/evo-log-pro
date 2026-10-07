'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreCorrectiveAction } from '@/components/qhse-securite/registres';

export default function PageCorrectiveAction() {
  return <RegistreGenerique config={registreCorrectiveAction} />;
}
