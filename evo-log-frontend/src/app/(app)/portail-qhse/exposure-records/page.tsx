'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreQspExposureRecord } from '@/components/portail-qhse/registres_c';

export default function PageQspExposureRecord() {
  return <RegistreGenerique config={registreQspExposureRecord} />;
}
