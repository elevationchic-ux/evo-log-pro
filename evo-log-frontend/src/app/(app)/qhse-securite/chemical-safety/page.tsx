'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreSafetyDataSheet } from '@/components/qhse-securite/registres';

export default function PageSafetyDataSheet() {
  return <RegistreGenerique config={registreSafetyDataSheet} />;
}
