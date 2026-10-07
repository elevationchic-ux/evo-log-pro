'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreHeavy2CraneSetupRecord } from '@/components/convoi-exceptionnel/registres_e';

export default function PageHeavy2CraneSetupRecord() {
  return <RegistreGenerique config={registreHeavy2CraneSetupRecord} />;
}
