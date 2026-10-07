'use client';
import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';
import { registreTechCalibrationRecord } from '@/components/portail-technicien/registres_c';

export default function PageTechCalibrationRecord() {
  return <RegistreGenerique config={registreTechCalibrationRecord} />;
}
