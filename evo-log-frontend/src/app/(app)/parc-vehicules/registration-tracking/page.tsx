'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreRegistrationRecord } from '@/components/parc-vehicules/registres';

export default function PageRegistrationRecord() {
  return <RegistreGenerique config={registreRegistrationRecord} />;
}
