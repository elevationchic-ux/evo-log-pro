'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreOperationalAlert } from '@/components/dashboard/registres';

export default function PageOperationalAlert() {
  return <RegistreGenerique config={registreOperationalAlert} />;
}
