'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQhseTrainingRecord } from '@/components/qhse-securite/registres_b';

export default function PageQhseTrainingRecord() {
  return <RegistreGenerique config={registreQhseTrainingRecord} />;
}
